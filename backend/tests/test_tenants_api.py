"""
租户 API 路由的单元测试
"""

import pytest
from fastapi.testclient import TestClient

from app.gateway.app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    return TestClient(app)


class TestTenantsAPI:
    """租户 API 端点测试"""

    def _get_csrf_token(self, client: TestClient) -> str:
        """获取CSRF token"""
        import secrets

        # 直接生成 CSRF token
        csrf_token = secrets.token_urlsafe(32)
        # 将 token 设置到 client 的 cookies 中
        client.cookies.set("csrf_token", csrf_token)
        return csrf_token

    def test_get_all_tenants(self, client):
        """测试获取所有租户"""
        response = client.get("/api/tenants")

        assert response.status_code == 200
        data = response.json()

        assert "tenants" in data
        assert "total" in data
        assert isinstance(data["tenants"], list)
        assert data["total"] > 0

        # 验证租户结构
        if data["tenants"]:
            tenant = data["tenants"][0]
            assert "id" in tenant
            assert "name" in tenant
            assert "status" in tenant
            assert "created_at" in tenant

    def test_get_current_tenant(self, client):
        """测试获取当前租户"""
        response = client.get("/api/tenants/current")

        assert response.status_code == 200
        tenant = response.json()

        assert "id" in tenant
        assert "name" in tenant
        assert tenant["status"] in ["active", "inactive"]
        assert "created_at" in tenant

    def test_get_tenant_by_id(self, client):
        """测试通过ID获取特定租户"""
        # 首先获取租户列表
        list_response = client.get("/api/tenants")
        assert list_response.status_code == 200

        tenants = list_response.json()["tenants"]
        if not tenants:
            pytest.skip("No tenants available for testing")

        # 获取第一个租户
        tenant_id = tenants[0]["id"]
        response = client.get(f"/api/tenants/{tenant_id}")

        assert response.status_code == 200
        tenant = response.json()

        assert tenant["id"] == tenant_id
        assert "name" in tenant
        assert "status" in tenant

    def test_get_nonexistent_tenant(self, client):
        """测试获取不存在的租户"""
        response = client.get("/api/tenants/nonexistent-tenant-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_switch_tenant(self, client):
        """测试切换租户"""
        # 首先获取租户列表
        list_response = client.get("/api/tenants")
        assert list_response.status_code == 200

        tenants = list_response.json()["tenants"]
        active_tenants = [t for t in tenants if t["status"] == "active"]

        if len(active_tenants) < 2:
            pytest.skip("Need at least 2 active tenants for this test")

        target_tenant_id = active_tenants[1]["id"]

        # 获取CSRF token
        csrf_token = self._get_csrf_token(client)

        # 切换租户
        response = client.post(f"/api/tenants/{target_tenant_id}/switch", headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 200
        tenant = response.json()
        assert tenant["id"] == target_tenant_id
        assert tenant["status"] == "active"

        # 验证当前租户已更改
        current_response = client.get("/api/tenants/current")
        assert current_response.status_code == 200
        current = current_response.json()
        assert current["id"] == target_tenant_id

    def test_switch_nonexistent_tenant(self, client):
        """测试切换不存在的租户"""
        csrf_token = self._get_csrf_token(client)
        response = client.post("/api/tenants/nonexistent-tenant-id/switch", headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 404

    def test_switch_inactive_tenant(self, client):
        """测试切换不活跃的租户"""
        # 首先获取租户列表
        list_response = client.get("/api/tenants")
        assert list_response.status_code == 200

        tenants = list_response.json()["tenants"]
        inactive_tenants = [t for t in tenants if t["status"] == "inactive"]

        if not inactive_tenants:
            pytest.skip("No inactive tenants available for testing")

        inactive_tenant_id = inactive_tenants[0]["id"]

        # 获取CSRF token
        csrf_token = self._get_csrf_token(client)

        # 尝试切换到不活跃租户
        response = client.post(f"/api/tenants/{inactive_tenant_id}/switch", headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_create_tenant(self, client):
        """测试创建新租户"""
        csrf_token = self._get_csrf_token(client)
        new_tenant_data = {
            "name": "测试租户",
            "description": "这是一个测试租户",
        }

        response = client.post("/api/tenants", json=new_tenant_data, headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 200
        tenant = response.json()

        assert tenant["name"] == "测试租户"
        assert tenant["description"] == "这是一个测试租户"
        assert tenant["status"] == "active"
        assert "id" in tenant
        assert "created_at" in tenant

    def test_create_tenant_without_description(self, client):
        """测试创建不带描述的租户"""
        csrf_token = self._get_csrf_token(client)
        new_tenant_data = {"name": "测试租户 2"}

        response = client.post("/api/tenants", json=new_tenant_data, headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 200
        tenant = response.json()

        assert tenant["name"] == "测试租户 2"
        assert "id" in tenant

    def test_update_tenant(self, client):
        """测试更新租户"""
        # 首先创建一个租户
        csrf_token = self._get_csrf_token(client)
        create_response = client.post("/api/tenants", json={"name": "原始名称", "description": "原始描述"}, headers={"X-CSRF-Token": csrf_token})
        assert create_response.status_code == 200
        tenant_id = create_response.json()["id"]

        # 更新租户
        update_csrf_token = self._get_csrf_token(client)
        update_data = {
            "name": "更新的名称",
            "description": "更新的描述",
        }
        response = client.put(f"/api/tenants/{tenant_id}", json=update_data, headers={"X-CSRF-Token": update_csrf_token})

        assert response.status_code == 200
        updated_tenant = response.json()

        assert updated_tenant["name"] == "更新的名称"
        assert updated_tenant["description"] == "更新的描述"
        assert updated_tenant["id"] == tenant_id

    def test_update_nonexistent_tenant(self, client):
        """测试更新不存在的租户"""
        csrf_token = self._get_csrf_token(client)
        update_data = {"name": "新名称"}

        response = client.put("/api/tenants/nonexistent-tenant-id", json=update_data, headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 404

    def test_delete_tenant(self, client):
        """测试删除租户"""
        # 首先创建一个租户
        csrf_token = self._get_csrf_token(client)
        create_response = client.post("/api/tenants", json={"name": "要删除的租户", "description": "这个租户将被删除"}, headers={"X-CSRF-Token": csrf_token})
        assert create_response.status_code == 200
        tenant_id = create_response.json()["id"]

        # 删除租户
        delete_csrf_token = self._get_csrf_token(client)
        response = client.delete(f"/api/tenants/{tenant_id}", headers={"X-CSRF-Token": delete_csrf_token})

        assert response.status_code == 204

        # 验证租户已删除
        get_response = client.get(f"/api/tenants/{tenant_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_tenant(self, client):
        """测试删除不存在的租户"""
        csrf_token = self._get_csrf_token(client)
        response = client.delete("/api/tenants/nonexistent-tenant-id", headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 404

    def test_delete_current_tenant(self, client):
        """测试删除当前活跃租户"""
        # 获取当前租户
        current_response = client.get("/api/tenants/current")
        assert current_response.status_code == 200
        current_tenant_id = current_response.json()["id"]

        # 获取CSRF token
        csrf_token = self._get_csrf_token(client)

        # 尝试删除当前租户
        response = client.delete(f"/api/tenants/{current_tenant_id}", headers={"X-CSRF-Token": csrf_token})

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestTenantsAPIIntegration:
    """租户 API 集成测试"""

    def _get_csrf_token(self, client: TestClient) -> str:
        """获取CSRF token"""
        import secrets

        # 直接生成 CSRF token
        csrf_token = secrets.token_urlsafe(32)
        # 将 token 设置到 client 的 cookies 中
        client.cookies.set("csrf_token", csrf_token)
        return csrf_token

    def test_full_tenant_workflow(self, client):
        """测试完整的租户工作流"""
        # 1. 获取初始租户列表
        initial_response = client.get("/api/tenants")
        assert initial_response.status_code == 200
        initial_count = initial_response.json()["total"]

        # 2. 创建新租户
        csrf_token = self._get_csrf_token(client)
        new_tenant_response = client.post("/api/tenants", json={"name": "工作流测试租户", "description": "用于测试工作流的租户"}, headers={"X-CSRF-Token": csrf_token})
        assert new_tenant_response.status_code == 200
        new_tenant = new_tenant_response.json()
        new_tenant_id = new_tenant["id"]

        # 3. 验证租户已创建
        list_response = client.get("/api/tenants")
        assert list_response.status_code == 200
        assert list_response.json()["total"] == initial_count + 1

        # 4. 获取新租户
        get_response = client.get(f"/api/tenants/{new_tenant_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == new_tenant_id

        # 5. 更新租户
        csrf_token = self._get_csrf_token(client)
        update_response = client.put(f"/api/tenants/{new_tenant_id}", json={"name": "更新的工作流租户"}, headers={"X-CSRF-Token": csrf_token})
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "更新的工作流租户"

        # 6. 如果租户是活跃的，尝试切换到它
        if get_response.json()["status"] == "active":
            csrf_token = self._get_csrf_token(client)
            switch_response = client.post(f"/api/tenants/{new_tenant_id}/switch", headers={"X-CSRF-Token": csrf_token})
            assert switch_response.status_code == 200

            # 验证已切换
            current_response = client.get("/api/tenants/current")
            assert current_response.status_code == 200
            assert current_response.json()["id"] == new_tenant_id

        # 7. 删除租户（除非是当前租户）
        if new_tenant_id != client.get("/api/tenants/current").json()["id"]:
            csrf_token = self._get_csrf_token(client)
            delete_response = client.delete(f"/api/tenants/{new_tenant_id}", headers={"X-CSRF-Token": csrf_token})
            assert delete_response.status_code == 204

            # 验证租户已删除
            final_get_response = client.get(f"/api/tenants/{new_tenant_id}")
            assert final_get_response.status_code == 404

    def test_tenant_listing_and_filtering(self, client):
        """测试租户列表和过滤"""
        # 获取所有租户
        response = client.get("/api/tenants")
        assert response.status_code == 200

        data = response.json()
        tenants = data["tenants"]

        assert len(tenants) > 0

        # 验证所有租户都有必需字段
        for tenant in tenants:
            assert "id" in tenant
            assert "name" in tenant
            assert "status" in tenant
            assert "created_at" in tenant

        # 检查状态值是否有效
        valid_statuses = {"active", "inactive"}
        for tenant in tenants:
            assert tenant["status"] in valid_statuses
