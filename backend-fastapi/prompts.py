from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template(
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|> \
{llm_instructions} {context}<|eot_id|><|start_header_id|>user<|end_header_id|> \
{question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>"
)


class Prompt:
    def __init__(self, llm_instructions, context, question):
        self.llm_instructions = llm_instructions
        self.context = context
        self.question = question
        self.prompt = prompt_template.format(llm_instructions=llm_instructions, context=context, question=question)


PROMPTS = [
    {
        "llm_instructions": "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им. \
Ты получаешь на вход транскрибированный текст переговоров машиниста с диспетчером. В их диалоге не должно присутствовать слов 'Здравствуйте', 'Спасибо', 'Пожалуйста'. \
Проанализируй заданный текст на наличие таких слов и выдай ответ в формате {'name_error': 'Нарушены правила служебных переговоров', 'text_error' : 'example string'}, где \
где поле text заменено на отрывок из текста, где была допущена ошибка. Если ошибки нет, выдай пустой массив '[]'. Ответ должен быть строго в указанном формате, \
 не должно быть никаких лишних слов!. Тщательно перепроверяй свой ответ на правильность. Вот текст, который тебе нужно анализировать: \n",
        "question": "Соблюдается в данном отрывке файла условие из контекста? \
         Сформируй вывод строго по инструкциям заданным в контексте!",
    },

    # {
    #     "llm_instructions": "",
    #     "question": "",
    # },
    #
    # {
    #     "llm_instructions": "",
    #     "question": "",
    # },
    #
    # {
    #     "llm_instructions": "",
    #     "question": "",
    # },

]
