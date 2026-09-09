VALID_STATUSES = {"pending", "in_progress", "done", "cancelled"}
VALID_ROLES = {"user", "admin", "manager"}
MIN_PASSWORD_LENGTH = 8


def validate_task_input(data, partial=False):
    if not data:
        return "Dados inválidos"
    if not partial and not data.get("title"):
        return "Título é obrigatório"
    if "title" in data and (not isinstance(data["title"], str) or not 3 <= len(data["title"].strip()) <= 200):
        return "Título deve ter entre 3 e 200 caracteres"
    if "status" in data and data["status"] not in VALID_STATUSES:
        return "Status inválido"
    if "priority" in data and (not isinstance(data["priority"], int) or not 1 <= data["priority"] <= 5):
        return "Prioridade deve ser entre 1 e 5"
    return None


def validate_password(password):
    return bool(password) and len(password) >= MIN_PASSWORD_LENGTH
