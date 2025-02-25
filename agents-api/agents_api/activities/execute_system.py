from typing import Any
from uuid import UUID

from beartype import beartype
from temporalio import activity

from ..autogen.Tools import SystemDef
from ..common.protocol.tasks import StepContext
from ..env import testing
from ..models.agent.create_agent import create_agent as create_agent_query
from ..models.agent.delete_agent import delete_agent as delete_agent_query
from ..models.agent.get_agent import get_agent as get_agent_query
from ..models.agent.list_agents import list_agents as list_agents_query
from ..models.agent.update_agent import update_agent as update_agent_query
from ..models.docs.create_doc import create_doc as create_doc_query
from ..models.docs.delete_doc import delete_doc as delete_doc_query
from ..models.docs.get_doc import get_doc as get_doc_query
from ..models.docs.list_docs import list_docs as list_docs_query
from ..models.session.create_session import create_session as create_session_query
from ..models.session.delete_session import delete_session as delete_session_query
from ..models.session.get_session import get_session as get_session_query
from ..models.session.list_sessions import list_sessions as list_sessions_query
from ..models.session.update_session import update_session as update_session_query
from ..models.task.create_task import create_task as create_task_query
from ..models.task.delete_task import delete_task as delete_task_query
from ..models.task.get_task import get_task as get_task_query
from ..models.task.list_tasks import list_tasks as list_tasks_query
from ..models.task.update_task import update_task as update_task_query
from ..models.user.create_user import create_user as create_user_query
from ..models.user.delete_user import delete_user as delete_user_query
from ..models.user.get_user import get_user as get_user_query
from ..models.user.list_users import list_users as list_users_query
from ..models.user.update_user import update_user as update_user_query


@beartype
async def execute_system(
    context: StepContext,
    system: SystemDef,
) -> Any:
    arguments = system.arguments
    arguments["developer_id"] = context.execution_input.developer_id

    # Convert all UUIDs to UUID objects
    if "agent_id" in arguments:
        arguments["agent_id"] = UUID(arguments["agent_id"])
    if "user_id" in arguments:
        arguments["user_id"] = UUID(arguments["user_id"])
    if "task_id" in arguments:
        arguments["task_id"] = UUID(arguments["task_id"])
    if "session_id" in arguments:
        arguments["session_id"] = UUID(arguments["session_id"])
    if "doc_id" in arguments:
        arguments["doc_id"] = UUID(arguments["doc_id"])

    # FIXME: This is a total mess. Should be refactored.
    try:
        # AGENTS
        if system.resource == "agent":
            # DOCS SUBRESOURCE
            if system.subresource == "doc":
                # Define the arguments for the agent doc queries
                agent_doc_args = {
                    **{
                        "owner_type": "agent",
                        "owner_id": arguments.pop("agent_id"),
                    },
                    **arguments,
                }
                if system.operation == "list":
                    return list_docs_query(**agent_doc_args)
                elif system.operation == "create":
                    return create_doc_query(**agent_doc_args)
                elif system.operation == "delete":
                    return delete_doc_query(**agent_doc_args)

            # NO SUBRESOURCE
            elif system.subresource == None:
                if system.operation == "list":
                    return list_agents_query(**arguments)
                elif system.operation == "get":
                    return get_agent_query(**arguments)
                elif system.operation == "create":
                    return create_agent_query(**arguments)
                elif system.operation == "update":
                    return update_agent_query(**arguments)
                elif system.operation == "delete":
                    return delete_agent_query(**arguments)

        # USERS
        elif system.resource == "user":
            # DOCS SUBRESOURCE
            if system.subresource == "doc":
                # Define the arguments for the user doc queries
                user_doc_args = {
                    **{
                        "owner_type": "user",
                        "owner_id": arguments.pop("user_id"),
                    },
                    **arguments,
                }
                if system.operation == "list":
                    return list_docs_query(**user_doc_args)
                elif system.operation == "create":
                    return create_doc_query(**user_doc_args)
                elif system.operation == "delete":
                    return delete_doc_query(**user_doc_args)

            # NO SUBRESOURCE
            elif system.subresource == None:
                if system.operation == "list":
                    return list_users_query(**arguments)
                elif system.operation == "get":
                    return get_user_query(**arguments)
                elif system.operation == "create":
                    return create_user_query(**arguments)
                elif system.operation == "update":
                    return update_user_query(**arguments)
                elif system.operation == "delete":
                    return delete_user_query(**arguments)

        # SESSIONS
        elif system.resource == "session":
            if system.operation == "list":
                return list_sessions_query(**arguments)
            elif system.operation == "get":
                return get_session_query(**arguments)
            elif system.operation == "create":
                return create_session_query(**arguments)
            elif system.operation == "update":
                return update_session_query(**arguments)
            elif system.operation == "delete":
                return update_session_query(**arguments)
            elif system.operation == "delete":
                return delete_session_query(**arguments)
        # TASKS
        elif system.resource == "task":
            if system.operation == "list":
                return list_tasks_query(**arguments)
            elif system.operation == "get":
                return get_task_query(**arguments)
            elif system.operation == "create":
                return create_task_query(**arguments)
            elif system.operation == "update":
                return update_task_query(**arguments)
            elif system.operation == "delete":
                return delete_task_query(**arguments)

        raise NotImplementedError(f"System call not implemented for {
                                  system.resource}.{system.operation}")

    except BaseException as e:
        if activity.in_activity():
            activity.logger.error(f"Error in execute_system_call: {e}")
        raise


# Mock and activity definition
mock_execute_system = execute_system

execute_system = activity.defn(name="execute_system")(
    execute_system if not testing else mock_execute_system
)
