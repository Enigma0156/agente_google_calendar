import os
import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage


try:
    from meu_agente import agente_google_calendar
except Exception as e:
    print(f"Erro crítico ao importar 'meu_agente': {e}")
    raise RuntimeError(f"Falha ao carregar o agente. Verifique as variáveis de ambiente. Erro: {e}")



class AgenteRequest(BaseModel):
    """O JSON que o n8n ou outro cliente deverá enviar."""
    prompt: str
    thread_id: str  

class AgenteResponse(BaseModel):
    """O JSON que sua API irá retornar."""
    resposta: str


app = FastAPI(
    title="API do Agente Google Calendar",
    description="Um endpoint para interagir com o agente LangGraph via HTTP.",
)



@app.get("/")
def read_root():
    return {"status": "API do Agente Google Calendar está online"}

@app.post("/invocar_agente", response_model=AgenteResponse)
async def invocar_agente(request: AgenteRequest):
    """
    Recebe um prompt e um ID de conversa, e retorna a resposta do agente.
    """
    if not request.prompt or not request.thread_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Os campos 'prompt' e 'thread_id' são obrigatórios."
        )

    print(f"Recebida requisição para thread_id: {request.thread_id}")

   
    config = {"configurable": {"thread_id": request.thread_id}}
    
   
    input_data = {"messages": [HumanMessage(content=request.prompt)]}

    try:
        
        resposta = await agente_google_calendar.ainvoke(input_data, config=config)
        
        
        if "messages" not in resposta or not isinstance(resposta["messages"], list) or len(resposta["messages"]) == 0:
            raise ValueError("A resposta do agente não contém 'messages' ou está vazia.")

        final_answer = resposta["messages"][-1].content
        print(f"Agente respondeu com sucesso para thread_id: {request.thread_id}")
        
        return AgenteResponse(resposta=final_answer)

    except Exception as e:
        print(f"Erro ao invocar o agente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro interno no servidor: {e}"
        )


if __name__ == "__main__":
    print("Iniciando servidor localmente em http://127.0.0.1:8000")
    # O Render ignora isso e usa o "Start Command"
    uvicorn.run(app, host="127.0.0.1", port=8000)