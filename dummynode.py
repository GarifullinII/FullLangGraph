from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class UserState(TypedDict):
    age: int
    message: str


def check_age(state: UserState) -> str:
    """Условная функция для проверки возраста"""
    return "совершеннолетний" if state["age"] >= 18 else "не_совершеннолетний"


def generate_success_message(state: UserState) -> dict:
    """Генерирует сообщение для совершеннолетних"""
    return {"message": f"Вам уже {state['age']} лет и вы можете водить!"}


def generate_failure_message(state: UserState) -> dict:
    """Генерирует сообщение для несовершеннолетних"""
    return {"message": f"Вам ещё только {state['age']} лет и вы не можете водить."}


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


# Фиктивный узел - просто передаёт состояние дальше
graph.add_node("fake_node", lambda state: state)


# Основные узлы обработки
graph.add_node("generate_success_message", generate_success_message)
graph.add_node("generate_failure_message", generate_failure_message)


# Связываем START с фиктивным узлом
graph.add_edge(START, "fake_node")


# От фиктивного узла идёт условное ребро
graph.add_conditional_edges(
    "fake_node", 
    check_age, 
    {
        "совершеннолетний": "generate_success_message",
        "не_совершеннолетний": "generate_failure_message"
    }
)


# Завершаем оба пути
graph.add_edge("generate_success_message", END)
graph.add_edge("generate_failure_message", END)


app = graph.compile()


gen_png_graph(app, name_photo="graph_example_2.png")
print("Граф сохранён как graph_example_2.png")


# Тест для несовершеннолетнего
result_minor = app.invoke({"age": 17})
print("Результат для 17 лет:", result_minor)


# Тест для совершеннолетнего  
result_adult = app.invoke({"age": 25})
print("Результат для 25 лет:", result_adult)
