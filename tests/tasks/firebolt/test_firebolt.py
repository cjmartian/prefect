from unittest.mock import MagicMock
import pytest
import firebolt.db.connection as fb_conn
from prefect.tasks.firebolt.firebolt import FireboltQuery


@pytest.fixture
def mock_conn(monkeypatch):

    # returns a mocked cursor for testing
    firebolt_conn = MagicMock()
    connection = MagicMock(spec=fb_conn.Connection)
    cursor = MagicMock(spec=fb_conn.Cursor)

    # link all the mocks together appropriately
    firebolt_conn.return_value = connection
    connection.cursor = cursor
    firebolt_connection = MagicMock(connect=firebolt_conn)
    monkeypatch.setattr(
        "prefect.tasks.firebolt.firebolt.firebolt_conn", firebolt_connection
    )

    return firebolt_connection, cursor


class TestFireboltQuery:
    def test_construction(self):
        """
        Tests that all required params are present for FireboltQuery Task.
        """
        task = FireboltQuery(
            database="test",
            username="test",
            password="test",
            engine_name="test",
            query="test",
        )
        assert task.database == "test"
        assert task.username == "test"
        assert task.password == "test"
        assert task.engine_name == "test"
        assert task.query == "test"

    def test_required_params(self):
        """
        Tests to check if there are missing required parameters.
        """

        # raises Value error if engine name is not provided
        with pytest.raises(ValueError, match="An engine name must be provided"):
            FireboltQuery().run(
                database="test",
                username="test",
                password="test",
                query="test",
            )

        # raises Value error if database name is not provided
        with pytest.raises(ValueError, match="A database name must be provided"):
            FireboltQuery().run(
                username="test",
                password="test",
                engine_name="test",
                query="test",
            )
        # raises Value error if username is not provided
        with pytest.raises(ValueError, match="User name must be provided"):
            FireboltQuery().run(
                database="test",
                password="test",
                engine_name="test",
                query="test",
            )

        # raises Value error if password is not provided
        with pytest.raises(ValueError, match="A password must be provided"):
            FireboltQuery().run(
                database="test",
                username="test",
                engine_name="test",
                query="test",
            )

        # raises Value error if query is not provided
        with pytest.raises(ValueError, match="A query string must be provided"):
            FireboltQuery().run(
                database="test",
                username="test",
                password="test",
                engine_name="test",
            )

    # test to check if the ddl/dml query was executed
    def test_execute_query(self, mock_conn):
        """
        Tests that the FireboltQuery Task calls the execute method on the cursor.
        """
        connection = mock_conn[0]
        cursor = mock_conn[1]

        # setting execute return
        cursor().__enter__().execute.return_value = 0
        query = "SHOW DATABASES"
        output = FireboltQuery(
            database="test",
            username="test",
            password="test",
            engine_name="test",
            query=query,
        ).run()
        conn_config = {
            "database": "test",
            "username": "test",
            "password": "test",
            "engine_name": "test",
        }
        connection.connect.assert_called_once_with(**conn_config)
        cursor.assert_called_with()
        cursor().__enter__().execute.assert_called_once_with(query)
        cursor().__enter__().fetchall.assert_not_called()
        assert output == []

    # test to check if the query was executed and metadata was retrieved from database
    def test_execute_fetchall(self, mock_conn):
        """
        Tests that the FireboltQuery Task calls the fetchall method on the cursor.
        """
        connection = mock_conn[0]
        cursor = mock_conn[1]

        # setting execute return
        cursor().__enter__().execute.return_value = 1

        # setting fetchall return
        cursor().__enter__().fetchall.return_value = ["TESTDB"]
        query = "SHOW DATABASES"
        output = FireboltQuery(
            database="test",
            username="test",
            password="test",
            engine_name="test",
            query=query,
        ).run()
        conn_config = {
            "database": "test",
            "username": "test",
            "password": "test",
            "engine_name": "test",
        }
        connection.connect.assert_called_once_with(**conn_config)
        cursor.assert_called_with()
        cursor().__enter__().execute.assert_called_once_with(query)
        cursor().__enter__().fetchall.assert_called()
        assert output == ["TESTDB"]
