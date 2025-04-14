from langchain_core.messages import HumanMessage

import chainlit as cl

from meu_agente import agente_google_calendar

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Agendamento de Evento",
            message="Poderia me ajudar com o agendamento de um evento para daqui três dias?",
            ),

        cl.Starter(
            label="Consultar Agenda de Amanhã",
            message="Eu preciso saber quais são meus compromissos de amanhã.",
            ),
        cl.Starter(
            label="Verificar Disponibilidade as 15hrs",
            message="Na semana que vem quais dias eu tenho disponibilidade para agendar uma reunião as 15hrs?.",
            ),
        ]


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    resposta = agente_google_calendar.invoke({"messages": [HumanMessage(content=msg.content)]}, config=config)
    final_answer = cl.Message(content=resposta["messages"][-1].content)
    await final_answer.send()
