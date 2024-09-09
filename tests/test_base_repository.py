import pytest
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from src.app.core.base_repository import GenericAsyncRepository
from tests.conftest import Base


class TestModel(Base):
    __test__ = False
    __tablename__ = "test_model"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class TestSchema(BaseModel):
    __test__ = False

    id: int | None
    name: str


class TestCreateSchema(BaseModel):
    __test__ = False

    name: str


class TestRepository(GenericAsyncRepository[TestModel]):
    __test__ = False
    pass


@pytest.fixture(scope="function")
async def repository(async_session):
    return TestRepository(TestModel, async_session)


async def test_create(repository):
    # Test creating an item
    item = TestCreateSchema(name="Test Item")
    created_item = await repository.create(item)
    assert created_item.id is not None
    assert created_item.name == "Test Item"


async def test_get_by_id(repository):
    # Create an item
    item = TestSchema(id=1, name="Test Item")
    created_item = await repository.create(item)

    # Test getting the item by id
    retrieved_item = await repository.get_by_id(created_item.id)
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.name == "Test Item"


async def test_get_all(repository):
    items = [TestSchema(id=i, name=f"Item {i}") for i in range(5)]
    for item in items:
        await repository.create(item)

    all_items = await repository.get_all(skip=0, limit=10)
    assert len(all_items) == 5
    assert all(isinstance(item, TestModel) for item in all_items)


async def test_update(repository):
    item = TestSchema(id=1, name="Original Name")
    created_item = await repository.create(item)

    updated_item = TestSchema(id=1, name="Updated Name")
    result = await repository.update(created_item.id, updated_item)

    assert result.id == created_item.id
    assert result.name == "Updated Name"


async def test_delete(repository):
    item = TestSchema(id=1, name="To Be Deleted")
    created_item = await repository.create(item)

    await repository.delete(created_item.id)

    deleted_item = await repository.get_by_id(created_item.id)
    assert deleted_item is None


async def test_create_many(repository):
    items = [TestSchema(id=i+i, name=f"Bulk Item {i}") for i in range(3)]
    created_items = await repository.create_many(items)

    assert len(created_items) == 3
    assert all(item.id is not None for item in created_items)
    assert [item.name for item in created_items] == ["Bulk Item 0", "Bulk Item 1", "Bulk Item 2"]


async def test_get_by_id_not_found(repository):
    non_existent_id = 9999
    result = await repository.get_by_id(non_existent_id)
    assert result is None


async def test_update_not_found(repository):
    non_existent_id = 9999
    update_data = TestSchema(id=1, name="Updated Name")

    with pytest.raises(ValueError, match=f"Item with id {non_existent_id} not found"):
        await repository.update(non_existent_id, update_data)


async def test_delete_not_found(repository):
    non_existent_id = 9999

    with pytest.raises(ValueError, match=f"Item with id {non_existent_id} not found"):
        await repository.delete(non_existent_id)
