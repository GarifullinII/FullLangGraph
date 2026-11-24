from typing import TypedDict
from datetime import date
from datetime import timedelta
from langgraph.graph import StateGraph, START, END


class UserState(TypedDict):
    name: str
    surname: str
    age: int
    birth_date: date
    today: date
    message: str


def calculate_age(state: UserState) -> dict:
    today = state["today"]
    age = today.year - state["birth_date"].year
    if (today.month, today.day) < (state["birth_date"].month, state["birth_date"].day):
        age -= 1
    return {"age": age}


def autoincrement_date(state: UserState) -> dict:
    """
    Увеличивает текущую дату на один день.
    """
    current_date = state["today"]
    new_date = current_date + timedelta(days=1)
    print(f"{current_date} -> {new_date}")
    return {"today": new_date}


def check_drive(state: UserState) -> str:
    if state["age"] >= 18:
        return "можно"
    else:
        return "нельзя"


def generate_success_message(state: UserState) -> dict:
    return {
        "message": f"Поздравляем, {state['name']} {state['surname']}! "
                   f"Вам уже {state['age']} лет и вы можете водить!"
    }


def generate_failure_message(state: UserState) -> dict:
    return {
        "message": f"К сожалению, {state['name']} {state['surname']}, "
                   f"вам ещё только {state['age']} лет и вы не можете водить."
    }


def gen_png_graph(app_obj, name_photo: str = "graph.png") -> None:
    """
    Генерирует PNG-изображение графа и сохраняет его в файл.
    
    Args:
        app_obj: Скомпилированный объект графа
        name_photo: Имя файла для сохранения (по умолчанию "graph.png")
    """
    with open(name_photo, "wb") as f:
        f.write(app_obj.get_graph().draw_mermaid_png())


graph = StateGraph(UserState)


graph.add_node("calculate_age", calculate_age)
graph.add_node("autoincrement_date", autoincrement_date)
graph.add_node("generate_success_message", generate_success_message)
graph.add_node("generate_failure_message", generate_failure_message)


graph.add_edge(START, "calculate_age")
graph.add_conditional_edges(
    "calculate_age", 
    check_drive, 
    {
        "можно": "generate_success_message", 
        "нельзя": "autoincrement_date"
    }
)
graph.add_edge("generate_success_message", END)
graph.add_edge("autoincrement_date", "calculate_age")


app = graph.compile()


# Генерируем визуализацию
gen_png_graph(app, name_photo="graph_example_1.png")
print("Граф сохранён как graph_example_1.png")


result = app.invoke({
    "name": "Алексей",
    "surname": "Яковенко",
    "birth_date": date.fromisoformat("2019-02-19"),
    "today": date.today()
},
config={"recursion_limit": 8000}
)


print(result)

