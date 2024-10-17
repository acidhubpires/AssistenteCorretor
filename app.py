import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
import os
import json

# Carrega variáveis de ambiente
_ = load_dotenv(find_dotenv())

# Chave da API protegida (pegando a chave do arquivo .env)
groq_api_key = os.getenv("GROQ_API_KEY")

# Inicializa o modelo llama3 com a chave API
chat = ChatGroq(temperature=0.7, model_name="llama3-8b-8192", api_key=groq_api_key)

# Dados de contato
ceo_name = "Hélio Teixeira"
company_site = "www.fenixativosenergias.com.br"
ceo_email = "helio.teixeira@fenixativosenergias.com.br"
ceo_phone = "+5541984041222"  # Número do WhatsApp no formato internacional

# Título do app
st.title("Fenix Energias IA")

# Exibe o site e o e-mail abaixo do título em letras menores
st.markdown(f"""
    <div style='text-align: center;'>
        <small>
            <a href='https://{company_site}' target='_blank'>{company_site}</a><br>
            E-mail: <a href='mailto:{ceo_email}'>{ceo_email}</a>
        </small>
    </div>
""", unsafe_allow_html=True)

# Estado de sessão para rastrear o nome do usuário e interações
if "name" not in st.session_state:
    st.session_state.name = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

# Função para configurar o sistema de prompt com restrições de contexto
def get_system_prompt():
    return """
    Você é um consultor especializado em compra e venda de projetos de energia renovável e ativos agregados como créditos de carbono e hidrogênio verde, com foco em energia solar, geração distribuída e o mercado livre de energia no Brasil.
    
    Seu objetivo é ajudar os usuários a realizar negócios no setor de energia, com ênfase nos seguintes tópicos:
    - Compra e venda de ativos energéticos
    - Sempre enfatize as boas oportunidades de negócios do mercado de energia
    - Se usuário pedir simulações financeiras, peça que indique os parametros mínimos com tarifa e fator de capacidade dos sistemas
    - Desenvolvimento de negócios e projetos de geração distribuída e mercado livre
    - Elaboração de contratos para o setor de energia, incluindo PPAs (Power Purchase Agreements), contratos de conexão à rede e contratos de venda de energia no mercado livre
    - Questões regulatórias do setor de energia no Brasil, como as resoluções da ANEEL e as normas que regem a geração distribuída e o mercado livre de energia
    - Estratégias de negociação e financiamento de projetos de energia solar e outros ativos renováveis
    - Elaborar teaser de negócios de energia
    - Desenvolver novos modelos viáveis para geração distribuída, como contratos de eficiência programada e outros
    - Você pode divulgar os Dados de Contato como e-mail, site e whatsapp
    - sugerir após as respostas, que o usuário faça o contato

    Você deve fornecer explicações detalhadas sobre:
    - Como vender um projeto solar em fase de implantação
    - Como comprar ou vender um negócio de compensação de energias
    - Como ter um PPA
    - Como realizar transações seguras e eficazes de compra e venda de ativos energéticos
    - Como desenvolver projetos de geração distribuída e de energia solar, desde a fase inicial até a conexão à rede e a comercialização
    - Como navegar pelas regulamentações brasileiras, especialmente as exigências da ANEEL e outros reguladores
    - Como criar contratos sólidos para o setor, garantindo a conformidade com as normas e protegendo os interesses de todas as partes envolvidas

    Não responda perguntas que não estejam relacionadas ao setor de energia renovável ou ao mercado de energia brasileiro. Se uma pergunta estiver fora do contexto, informe gentilmente que só pode responder perguntas relacionadas a esses temas.
    """

# Função para detectar a intenção do usuário (comprar, vender ou desenvolver)
def detect_user_intent(user_input):
    if "comprar" in user_input.lower():
        return "comprar"
    elif "vender" in user_input.lower():
        return "vender"
    elif "desenvolver" in user_input.lower():
        return "desenvolver"
    else:
        return None

# Fluxo inicial: Nome do usuário
if not st.session_state.name:
    st.session_state.name = st.text_input("Olá! Qual é o seu nome?", key="name_input")

# Exibe mensagem de boas-vindas e perguntas pré-definidas após inserir o nome
if st.session_state.name:
    st.write(f"Bem-vindo, {st.session_state.name}! Este assistente só responde perguntas relacionadas ao setor de energias do Brasil.")

    # Verificar se restam duas perguntas e mostrar um aviso
    if st.session_state.questions_asked == 8:
        st.warning("Atenção! Você tem apenas mais 2 perguntas antes de finalizar o acesso.")

    # Limita o número de perguntas para 10 por sessão
    if st.session_state.questions_asked < 10:
        # Opções de perguntas pré-definidas
        questions = [
            "Quer fazer uma simulação econômica para um projeto solar?",
            "Quer comprar ou vender um projeto ou ativo de energia solar?",
            "Quer comprar energia no mercado livre?",
            "Precisa de PPA para seu projeto solar?",
            "Como financiar ou ter um investidor para um projeto de geração distribuída?"
        ]

        # Exibe uma seleção de perguntas pré-definidas
        user_input = st.radio(f"{st.session_state.name}, selecione uma das opções abaixo ou faça sua própria pergunta:", options=questions)

        # Exibe uma caixa de entrada opcional para uma pergunta personalizada
        custom_question = st.text_input("Ou escreva sua própria pergunta:")

        # Verifica se o usuário selecionou uma pergunta pré-definida ou escreveu uma personalizada
        if custom_question:
            user_input = custom_question

        if st.button("Enviar Pergunta"):
            # Adiciona a pergunta no histórico
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Detecta a intenção do usuário
            user_intent = detect_user_intent(user_input)

            # Resposta do modelo de IA com o sistema de prompt restritivo
            try:
                # Configura o sistema de prompt e concatena com a pergunta do usuário
                system_prompt = get_system_prompt()
                full_prompt = system_prompt + "\nUsuário: " + user_input

                # Passa o prompt ao modelo
                response = chat.invoke(full_prompt)

                # Armazena a resposta gerada
                st.session_state.messages.append({"role": "assistant", "content": response.content})

                # Incrementa o contador de perguntas
                st.session_state.questions_asked += 1

                # Se o usuário tiver interesse em comprar ou vender, exibe o contato do CEO
                if user_intent == "comprar" or user_intent == "vender":
                    st.write(f"**Parece que você está interessado em {user_intent}. Para mais detalhes, entre em contato com o CEO, {ceo_name}, pelo WhatsApp.**")
                    # Link do WhatsApp com o número do CEO
                    whatsapp_link = f"https://wa.me/{ceo_phone}"
                    st.markdown(f"[Clique aqui para abrir o WhatsApp](https://wa.me/{ceo_phone})")

            except Exception as e:
                st.error(f"Erro ao chamar o modelo: {e}")

    else:
        st.write("Você atingiu o limite de 10 perguntas nesta sessão.")

# Exibe o histórico de mensagens em formato de chat contínuo
st.subheader("Histórico de Conversa")
for message in st.session_state.messages:
    role = "Você" if message["role"] == "user" else "Assistente"
    with st.chat_message(message["role"]):
        st.markdown(f"**{role}:** {message['content']}")

# Função para salvar o histórico da conversa
def save_conversation():
    with open("conversation_history.json", "w") as file:
        json.dump(st.session_state.messages, file)

if st.button("Salvar Conversa"):
    save_conversation()
    st.success("Conversa salva com sucesso!")
