"""
导入导出 API

支持：
- Postman Collection v2.1 导入
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import success, ResponseModel
from app.core.exceptions import NotFoundError, ValidationError
from app.models.project import Project
from app.models.module import Module
from app.models.test_case import TestCase
from app.models.environment import Environment, EnvVariable
from app.utils.postman_parser import parse_postman_collection, ParseResult

router = APIRouter(prefix="/import", tags=["导入导出"])


@router.post("/postman", response_model=ResponseModel)
async def import_postman_collection(
    file: UploadFile = File(..., description="Postman Collection JSON 文件"),
    project_id: int = Form(..., description="目标项目 ID"),
    module_id: Optional[int] = Form(None, description="目标模块 ID（可选，不指定则根据文件夹创建）"),
    create_environment: bool = Form(False, description="是否根据 Collection 变量创建环境"),
    db: AsyncSession = Depends(get_db),
):
    """
    导入 Postman Collection

    支持 Postman Collection v2.1 格式

    - 嵌套文件夹会转换为模块层级
    - 请求会转换为测试用例
    - Collection 变量可选择性创建为环境
    """
    # 验证项目存在
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError(f"项目不存在: {project_id}")

    # 如果指定了模块，验证模块存在且属于该项目
    target_module = None
    if module_id:
        target_module = await db.get(Module, module_id)
        if not target_module:
            raise NotFoundError(f"模块不存在: {module_id}")
        if target_module.project_id != project_id:
            raise ValidationError("模块不属于指定项目")

    # 读取并解析文件
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise ValidationError("文件编码错误，请使用 UTF-8 编码")
    except Exception as e:
        raise ValidationError(f"文件读取失败: {str(e)}")

    # 解析 Postman Collection
    result = parse_postman_collection(content_str)

    if result.errors and not result.requests:
        raise ValidationError(f"解析失败: {'; '.join(result.errors)}")

    # 统计信息
    stats = {
        "collection_name": result.collection_name,
        "total_requests": len(result.requests),
        "total_folders": len(result.folders),
        "success_count": 0,
        "failed_count": 0,
        "created_modules": [],
        "created_cases": [],
        "created_environment": None,
        "errors": result.errors.copy(),
    }

    # 创建模块映射（文件夹路径 -> 模块 ID）
    module_map = {}

    if target_module:
        # 如果指定了目标模块，所有用例都放入该模块
        module_map[tuple()] = target_module.id
    else:
        # 根据文件夹结构创建模块
        await _create_modules_from_folders(
            db, project_id, result.folders, module_map, stats
        )

        # 如果没有文件夹，创建一个默认模块
        if not result.folders and result.requests:
            default_module = Module(
                project_id=project_id,
                name=result.collection_name or "Imported",
                description=result.collection_description,
            )
            db.add(default_module)
            await db.flush()
            module_map[tuple()] = default_module.id
            stats["created_modules"].append({
                "id": default_module.id,
                "name": default_module.name,
            })

    # 创建测试用例
    for req in result.requests:
        try:
            # 确定所属模块
            folder_key = tuple(req.folder_path)

            # 查找最近的父级模块
            module_id_for_case = None
            while folder_key is not None:
                if folder_key in module_map:
                    module_id_for_case = module_map[folder_key]
                    break
                if folder_key:
                    folder_key = tuple(folder_key[:-1])
                else:
                    break

            if module_id_for_case is None:
                # 使用默认模块或第一个创建的模块
                if module_map:
                    module_id_for_case = list(module_map.values())[0]
                else:
                    stats["failed_count"] += 1
                    stats["errors"].append(f"用例 '{req.name}' 找不到目标模块")
                    continue

            # 创建测试用例
            test_case = TestCase(
                module_id=module_id_for_case,
                name=req.name,
                description=req.description,
                method=req.method,
                path=req.path,
                headers=req.headers,
                params=req.params,
                body_type=req.body_type,
                body_content=req.body_content,
            )
            db.add(test_case)
            await db.flush()

            stats["success_count"] += 1
            stats["created_cases"].append({
                "id": test_case.id,
                "name": test_case.name,
                "method": test_case.method,
                "path": test_case.path,
            })

        except Exception as e:
            stats["failed_count"] += 1
            stats["errors"].append(f"创建用例 '{req.name}' 失败: {str(e)}")

    # 可选：创建环境
    if create_environment and result.variables:
        try:
            env = Environment(
                project_id=project_id,
                name=f"{result.collection_name} - Variables",
                description=f"从 Postman Collection 导入的变量",
                base_url="",
            )
            db.add(env)
            await db.flush()

            for var in result.variables:
                env_var = EnvVariable(
                    environment_id=env.id,
                    key=var.key,
                    value=var.value,
                    description=f"Type: {var.type}",
                )
                db.add(env_var)

            await db.flush()

            stats["created_environment"] = {
                "id": env.id,
                "name": env.name,
                "variables_count": len(result.variables),
            }

        except Exception as e:
            stats["errors"].append(f"创建环境失败: {str(e)}")

    await db.commit()

    return success(data={
        "message": f"导入完成: 成功 {stats['success_count']} 个，失败 {stats['failed_count']} 个",
        "collection_name": stats["collection_name"],
        "success_count": stats["success_count"],
        "failed_count": stats["failed_count"],
        "created_modules": stats["created_modules"],
        "created_cases_count": len(stats["created_cases"]),
        "created_environment": stats["created_environment"],
        "errors": stats["errors"] if stats["errors"] else None,
    })


async def _create_modules_from_folders(
    db: AsyncSession,
    project_id: int,
    folders: list,
    module_map: dict,
    stats: dict,
):
    """
    根据文件夹结构创建模块

    Args:
        db: 数据库会话
        project_id: 项目 ID
        folders: 解析出的文件夹列表
        module_map: 路径到模块 ID 的映射（会被修改）
        stats: 统计信息（会被修改）
    """
    # 按路径深度排序，确保先创建父级
    sorted_folders = sorted(folders, key=lambda f: len(f.parent_path))

    for folder in sorted_folders:
        try:
            # 计算完整路径
            full_path = tuple(folder.parent_path + [folder.name])

            # 检查是否已存在
            if full_path in module_map:
                continue

            # 获取父级模块 ID
            parent_id = None
            if folder.parent_path:
                parent_path = tuple(folder.parent_path)
                parent_id = module_map.get(parent_path)

            # 创建模块
            module = Module(
                project_id=project_id,
                name=folder.name,
                description=folder.description,
                parent_id=parent_id,
            )
            db.add(module)
            await db.flush()

            module_map[full_path] = module.id
            stats["created_modules"].append({
                "id": module.id,
                "name": folder.name,
                "parent_id": parent_id,
            })

        except Exception as e:
            stats["errors"].append(f"创建模块 '{folder.name}' 失败: {str(e)}")


@router.post("/postman/preview", response_model=ResponseModel)
async def preview_postman_collection(
    file: UploadFile = File(..., description="Postman Collection JSON 文件"),
):
    """
    预览 Postman Collection 内容

    不实际导入，只返回解析结果预览
    """
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise ValidationError("文件编码错误，请使用 UTF-8 编码")
    except Exception as e:
        raise ValidationError(f"文件读取失败: {str(e)}")

    result = parse_postman_collection(content_str)

    if result.errors and not result.requests:
        raise ValidationError(f"解析失败: {'; '.join(result.errors)}")

    # 构建文件夹树
    folder_tree = _build_folder_tree(result.folders, result.requests)

    return success(data={
        "collection_name": result.collection_name,
        "collection_description": result.collection_description,
        "total_requests": len(result.requests),
        "total_folders": len(result.folders),
        "total_variables": len(result.variables),
        "folder_tree": folder_tree,
        "variables": [
            {"key": v.key, "value": v.value, "type": v.type}
            for v in result.variables
        ],
        "requests_preview": [
            {
                "name": r.name,
                "method": r.method,
                "path": r.path,
                "folder_path": r.folder_path,
            }
            for r in result.requests[:50]  # 最多预览 50 个
        ],
        "errors": result.errors if result.errors else None,
    })


def _build_folder_tree(folders: list, requests: list) -> list:
    """构建文件夹树结构"""
    tree = {}

    # 添加文件夹
    for folder in folders:
        path = tuple(folder.parent_path + [folder.name])
        node = tree
        for part in path:
            if part not in node:
                node[part] = {"_children": {}, "_requests": []}
            node = node[part]["_children"]

    # 添加请求到对应文件夹
    for req in requests:
        path = tuple(req.folder_path) if req.folder_path else tuple()
        node = tree
        for part in path:
            if part in node:
                node = node[part]["_children"]
            else:
                break
        else:
            # 找到正确的节点，但我们需要获取父级节点来添加请求
            pass

    # 简化输出
    def simplify_tree(node: dict, parent_path: list = None) -> list:
        if parent_path is None:
            parent_path = []
        result = []
        for name, data in node.items():
            if name.startswith("_"):
                continue
            current_path = parent_path + [name]
            # 计算这个文件夹下的请求数
            request_count = sum(
                1 for r in requests
                if r.folder_path == current_path
            )
            result.append({
                "name": name,
                "path": current_path,
                "request_count": request_count,
                "children": simplify_tree(data.get("_children", {}), current_path),
            })
        return result

    # 根级别请求
    root_requests = sum(1 for r in requests if not r.folder_path)

    return {
        "root_requests": root_requests,
        "folders": simplify_tree(tree),
    }
