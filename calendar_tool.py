from dotenv import load_dotenv
load_dotenv()

from typing import Annotated, Optional

from google_calendar_functions import cria_calendario, listar_calendarios, listar_eventos_calendario, criar_evento_programado, excluir_evento, atualizar_evento
from langchain_core.tools import tool


@tool
def criar_calendario_tool(
    calendar_name: Annotated[str, "Nome do calendário que será criado"],
    timezone: Annotated[str, "Fuso horário do calendário (padrão: America/Sao_Paulo)"] = "America/Sao_Paulo"
) -> str:
    """
    Cria um novo calendário utilizando a API do Google Calendar e retorna o ID do calendário criado.

    Parâmetros:
      calendar_name (str): Nome do calendário que será criado.
      timezone (str, opcional): Fuso horário a ser utilizado no calendário. O padrão é "America/Sao_Paulo".

    Retorno:
      str: Identificador do calendário criado, conforme retornado pela API.

    A função forma um dicionário com os dados do calendário e utiliza o método `insert` da API para
    criar o calendário. Em seguida, extrai e retorna o ID do calendário a partir da resposta.
    """
    print("Tool `criar_calendario` foi chamada.")
    calendar_id = cria_calendario(calendar_name, timezone)
    return f"Calendário criado.\n summary: '{calendar_name}' | calendar_id: '{calendar_id}'."

@tool
def listar_calendarios_tool(
    max_capacity: Annotated[int, "Número máximo de calendários a recuperar."] = 200
) -> list | str:
    """
    Recupera listas de calendários da conta do Google Calendar, respeitando o limite definido por max_capacity.

    Parâmetros:
      max_capacity (int, opcional): Número máximo de calendários a serem recuperados. Se fornecido como string, a função a converte para inteiro. O padrão é 200.

    Retorno:
      list: Uma lista de dicionários. Cada dicionário contém os dados formatados do calendário, com as seguintes chaves:
            - 'id': Identificador único do calendário.
            - 'name': Nome ou resumo do calendário.
            - 'description': Descrição do calendário (pode ser vazia).
            - 'primary': Indica se é o calendário principal (True ou False).
            - 'time_zone': Fuso horário associado ao calendário.
            - 'etag': Identificador de versão do calendário.
            - 'access_role': Papel de acesso do usuário ao calendário.

    Funcionamento:
      A função realiza chamadas paginadas à API do Google Calendar. Em cada iteração, são recuperados até 200 itens
      ou o número restante definido por max_capacity. O loop é interrompido quando o número total de itens recuperados
      atinge max_capacity ou quando não há mais páginas de resultados. Após a coleta, os dados de cada calendário são
      "limpos" para conter apenas os campos relevantes e retornados em uma lista.
    """
    try:
        print("Tool `listar_calendarios` foi chamada.")
        lista_de_calendarios = listar_calendarios(max_capacity)
        return lista_de_calendarios
    except Exception as e:
        return f"Falha na execução da ferramenta `listar_calendarios`. Erro: {e}"

@tool
def listar_eventos_calendario_tool(
    calendar_id: Annotated[str, "ID do calendário a ser consultado (padrão: 'primary')"] = 'primary',
    max_capacity: Annotated[int, "Número máximo de eventos a serem recuperados."] = 20,
    time_min: Annotated[Optional[str], "Data/hora mínima para o início dos eventos no formato RFC3339 (e.g., '2025-04-06T10:00:00-04:00')."] = None,
    time_max: Annotated[Optional[str], "Data/hora máxima para o término dos eventos no formato RFC3339 (e.g., '2025-04-06T10:00:00-04:00')."] = None,
    show_deleted: Annotated[bool, "Indica se eventos deletados devem ser incluídos na listagem."] = False
) -> list | str:
    """
        Recupera eventos de um calendário específico até atingir o número máximo de eventos definido (max_capacity).

        Parâmetros:
          calendar_id (str): ID do calendário do qual os eventos serão listados. O padrão é 'primary'.
          max_capacity (int): Número máximo de eventos a serem recuperados.
          time_min (str, opcional): Data/hora mínima para o início dos eventos no formato RFC3339.
          time_max (str, opcional): Data/hora máxima para o término dos eventos no formato RFC3339.
          show_deleted (bool): Define se a listagem deve incluir eventos deletados (False por padrão).

        Retorno:
          list: Uma lista de eventos processados. Cada evento é representado por um dicionário.

        Funcionamento:
          A função realiza uma consulta paginada na API do Google Calendar para recuperar os eventos do calendário
          especificado. Em cada iteração, é solicitada uma quantidade de eventos limitada pelo valor mínimo entre 250
          e a quantidade remanescente definida por max_capacity. O processo é repetido até que o total de eventos
          coletados alcance max_capacity ou não existam mais páginas de resultados. Ao final, os eventos são processados
          para extrair as informações relevantes e retornados em uma lista de dicionários.
        """
    try:
        print("Tool `listar_eventos_calendario` foi chamada.")
        lista_de_eventos = listar_eventos_calendario(calendar_id, max_capacity, time_min, time_max, show_deleted)
        return lista_de_eventos
    except Exception as e:
        return f"Falha na execução da ferramenta `listar_eventos_calendario`. Erro: {e}"

@tool
def criar_evento_programado_tool(
    start: Annotated[str, "Hora de início do evento no formato RFC3339 (ex.: '2025-04-06T10:00:00-04:00')"],
    end: Annotated[str, "Hora de término do evento no formato RFC3339 (ex.: '2025-04-06T11:00:00-04:00')"],
    calendar_id: Annotated[str, "ID do calendário onde o evento será criado (padrão: 'primary')"] = 'primary',
    timezone: Annotated[str, "Fuso horário do evento (ex.: 'America/Sao_Paulo')"] = "America/Sao_Paulo",
    summary: Annotated[str | None, "Título ou assunto breve do evento (opcional)"] = None,
    description: Annotated[str | None, "Descrição detalhada ou notas do evento (opcional)"] = None,
    location: Annotated[str | None, "Local físico ou virtual do evento (opcional)"] = None,
    attendees: Annotated[list | None, "Lista de endereços de e-mail dos participantes (opcional)"] = None,
    send_notifications: Annotated[bool, "Determina se notificações devem ser enviadas aos participantes"] = True,
) -> str:
    """
    Cria um evento no Google Calendar utilizando os detalhes fornecidos e retorna uma mensagem contendo o ID do evento criado.

    Parâmetros:
      start (str): Hora de início do evento no formato RFC3339 (ex.: '2025-04-06T10:00:00-04:00').
      end (str): Hora de término do evento no formato RFC3339 (ex.: '2025-04-06T11:00:00-04:00').
      calendar_id (str): ID do calendário onde o evento será criado. Padrão: 'primary'.
      timezone (str): Fuso horário do evento, conforme a base de dados IANA Time Zone (ex.: "America/Sao_Paulo").
      summary (str, opcional): Título ou assunto breve do evento.
      description (str, opcional): Descrição detalhada ou notas sobre o evento.
      location (str, opcional): Local físico ou virtual onde o evento ocorrerá.
      attendees (list, opcional): Lista de endereços de e-mail dos participantes.
      send_notifications (bool): Define se notificações devem ser enviadas aos participantes. Padrão: True.

    Retorno:
      str: Mensagem informando o sucesso da criação do evento (incluindo o ID do evento) ou uma mensagem de erro caso a criação falhe.

    Funcionamento:
      - Verifica se o serviço do Google Calendar está disponível.
      - Valida o formato das datas de início e término usando `datetime.fromisoformat`.
      - Monta o dicionário `event` com os campos obrigatórios de início e término, incluindo o fuso horário.
      - Adiciona opcionalmente os campos 'summary', 'description' e 'location', caso seus valores sejam fornecidos.
      - Se houver participantes, formata cada endereço de e-mail como um dicionário e adiciona à chave 'attendees'.
      - Tenta inserir o evento utilizando a API do Google Calendar e retorna uma mensagem com o ID do evento criado.
      - Em caso de falha na criação ou na comunicação com o serviço, retorna uma mensagem de erro apropriada.
    """
    print("Tool `criar_evento_programado` foi chamada.")
    evento_criado = criar_evento_programado(start, end, calendar_id, timezone, summary, description, location, attendees, send_notifications)
    return evento_criado


@tool
def excluir_evento_tool(
    event_id: Annotated[str, "ID do evento a ser excluído"],
    send_notifications: Annotated[bool, "Enviar notificações de cancelamento aos participantes"] = True,
    calendar_id: Annotated[str, "ID do calendário de onde o evento será excluído"] = "primary"
) -> str:
    """
    Exclui um evento do Google Calendar a partir do seu ID.

    Parâmetros:
      event_id (str): ID do evento que deverá ser excluído.
      send_notifications (bool): Indica se deve enviar notificações de cancelamento para os participantes.
                                  O valor padrão é True.
      calendar_id (str): ID do calendário de onde o evento será removido. O padrão é 'primary'.

    Retorno:
      bool: Retorna True se a exclusão do evento for bem-sucedida; caso ocorra alguma exceção, retorna False.

    Funcionamento:
      A função tenta excluir o evento chamando a API do Google Calendar. Se a requisição for executada
      sem problemas, a função retorna True. Se ocorrer qualquer erro durante a operação, o erro é
      impresso no console e a função retorna False.
    """
    print("Tool `excluir_evento` foi chamada.")
    resposta = excluir_evento(event_id, send_notifications, calendar_id)
    return resposta


@tool
def atualizar_evento_tool(
    event_id: Annotated[str, "ID do evento a ser atualizado"],
    calendar_id: Annotated[str, "ID do calendário onde o evento se encontra (padrão: 'primary')"] = 'primary',
    start: Annotated[Optional[str], "Nova data/hora de início do evento no formato ISO 8601 (ex.: '2025-04-06T10:00:00-04:00')"] = None,
    end: Annotated[Optional[str], "Nova data/hora de término do evento no formato ISO 8601 (ex.: '2025-04-06T11:00:00-04:00')"] = None,
    timezone: Annotated[Optional[str], "Novo fuso horário para o evento (formato IANA Time Zone)"] = "America/Sao_Paulo",
    summary: Annotated[Optional[str], "Novo título ou resumo do evento, se desejado"] = None,
    description: Annotated[Optional[str], "Nova descrição ou notas para o evento, se desejado"] = None,
    location: Annotated[Optional[str], "Nova localização física ou virtual para o evento, se desejado"] = None,
) -> str:
    """
    Atualiza um evento no Google Calendar substituindo os campos informados por novos valores.
    Os campos que não forem especificados permanecerão com seus valores atuais.

    Parâmetros:
      event_id (str): ID do evento que será atualizado.
      calendar_id (str): ID do calendário onde o evento se encontra. O padrão é 'primary'.
      start (str, opcional): Nova data/hora de início do evento no formato RFC3339 (ex.: '2025-04-06T10:00:00-04:00').
      end (str, opcional): Nova data/hora de término do evento no formato RFC3339 (ex.: '2025-04-06T11:00:00-04:00').
      timezone (str, opcional): Novo fuso horário para o evento, conforme o padrão IANA Time Zone (ex.: "America/Sao_Paulo").
      summary (str, opcional): Novo título ou resumo do evento.
      description (str, opcional): Nova descrição ou notas sobre o evento.
      location (str, opcional): Nova localização física ou virtual do evento.

    Retorno:
      str: Mensagem indicando se a atualização foi bem-sucedida, contendo o ID do evento e os campos atualizados, ou uma mensagem de erro caso a atualização não tenha sido realizada.

    Funcionamento:
      - Verifica a disponibilidade do serviço do Google Calendar.
      - Valida os formatos das novas datas/hora ('start' e 'end') para garantir que estejam em formato RFC3339.
      - Constrói um dicionário com os campos a serem atualizados com os novos valores informados.
      - Se o fuso horário (timezone) for fornecido, atualiza os campos 'start' e 'end' para incluir esta informação.
      - Realiza a atualização do evento utilizando o método 'patch' da API do Google Calendar.
      - Caso a atualização seja bem-sucedida, retorna uma mensagem contendo o ID do evento e os campos atualizados;
        caso contrário, retorna uma mensagem informando que o evento não pôde ser atualizado.
    """
    print("Tool `atualizar_evento` foi chamada.")
    resposta = atualizar_evento(event_id, calendar_id, start, end, timezone, summary, description, location)
    return resposta

