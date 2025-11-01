import os
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow # Importar no topo

# A variável 'RENDER' é definida automaticamente pelo Render
IS_RENDER = os.environ.get('RENDER') 

if IS_RENDER:
    # No Render, vamos ler os arquivos de /etc/secrets/
    SECRETS_DIR = '/etc/secrets'
    TOKEN_PATH = os.path.join(SECRETS_DIR, 'token_calendar_v3.json')
    CLIENT_SECRET_PATH = os.path.join(SECRETS_DIR, 'client_secret.json')
else:
    # Localmente, use a estrutura de pastas original
    TOKEN_DIR = 'token files'
    if not os.path.exists(TOKEN_DIR):
        os.mkdir(TOKEN_DIR)
    TOKEN_PATH = os.path.join(TOKEN_DIR, 'token_calendar_v3.json')
    # Use o nome do seu ficheiro de client_secret aqui
    CLIENT_SECRET_PATH = 'client_secret_1046410091087-c01jjcho4deuaoblpq3lhq367cga2ifj.apps.googleusercontent.com.json'


# A função agora IGNORA o primeiro argumento (client_secret_file_path_arg_IGNORED)
# e usa os caminhos globais que definimos acima
def create_service(client_secret_file_path_arg_IGNORED, api_name, api_version, *scopes, prefix=''):
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    cred = None
    
    # 1. Tentar carregar o token existente (do TOKEN_PATH)
    if os.path.exists(TOKEN_PATH):
        try:
            cred = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            print(f"Token carregado com sucesso de {TOKEN_PATH}")
        except Exception as e:
            print(f"Aviso: Erro ao carregar token de {TOKEN_PATH}: {e}")
            cred = None
    else:
        print(f"Aviso: Ficheiro de token não encontrado em {TOKEN_PATH}")

    # 2. Se o token não for válido ou não existir
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            print("Token expirado, tentando atualizar...")
            try:
                cred.refresh(Request())
            except Exception as e:
                print(f"Erro ao atualizar token: {e}")
                cred = None # Força re-autenticação se o refresh falhar
        
        # Se ainda não há 'cred' (seja por falha no refresh, ou por não existir)
        if not cred:
            # Se estamos no Render, é um erro fatal. Não há como autenticar.
            if IS_RENDER:
                print(f"ERRO FATAL: O token em '{TOKEN_PATH}' é inválido ou não existe.")
                print("Verifique se o 'Secret File' foi criado corretamente no Render.")
                return None
            
            # Se estiver local, rode o fluxo de autenticação
            print("Token inválido ou não encontrado. Iniciando fluxo de autenticação local...")
            
            # Usa o 'CLIENT_SECRET_PATH' GLOBAL, não o argumento
            if not os.path.exists(CLIENT_SECRET_PATH):
                    print(f"ERRO FATAL: 'client_secret' não encontrado em: {CLIENT_SECRET_PATH}")
                    print("Verifique o nome do ficheiro client_secret...json")
                    return None

            # O 'CLIENT_SECRET_PATH' global é usado aqui
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            cred = flow.run_local_server(port=0)
    
    # 3. Salvar o token (se foi atualizado ou criado E estamos local)
    if not IS_RENDER:
        try:
            with open(TOKEN_PATH, 'w') as token:
                token.write(cred.to_json())
            print(f"Token salvo/atualizado localmente em: {TOKEN_PATH}")
        except Exception as e:
            print(f"Aviso: Não foi possível salvar o token atualizado: {e}")

    # 4. Construir o serviço
    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred, static_discovery=False)
        print(f"{API_SERVICE_NAME} {API_VERSION} service created successfully")
        return service
    except Exception as e:
        print(f'Falha ao criar instância do serviço: {e}')
        return None