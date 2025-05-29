import functools
from win32api import MessageBox
from win32con import MB_OK, MB_ICONWARNING
# from DatabaseOperations import DatabaseOperations

def check_permission(criteria_name, required_type):
    """
    Decorator function to check permissions
    
    Args:
        criteria_name (str): The permission criteria (e.g., 'warehouses', 'accounts')
        required_type (str): The permission type ('r' or 'rw')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                # Get sql_connector and user_id from the instance (self)
                sql_connector = getattr(self, 'sql_connector', None)
                user_id = getattr(self, 'current_user', None)

                if not sql_connector:
                    raise ValueError("No sql_connector found in class instance")
                if not user_id:
                    raise ValueError("No user_id found in class instance")

                db = DatabaseOperations(sql_connector)
                has_permission = db.fetchUserPermission(
                    user_id, 
                    criteria_name, 
                    required_type
                )

                if not has_permission:
                    MessageBox(
                        None, 
                        f"You don't have {required_type} permission for {criteria_name}",
                        "Permission Denied",
                        MB_OK | MB_ICONWARNING
                    )
                    return None

                return func(self, *args, **kwargs)

            except Exception as e:
                MessageBox(
                    None,
                    f"Permission check failed: {str(e)}",
                    "Error",
                    MB_OK | MB_ICONWARNING
                )
                return None

        return wrapper
    return decorator