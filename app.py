import streamlit as st
import pandas as pd
import datetime
import uuid
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Recebimento - Suzano",
    page_icon="📦",
    layout="wide"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    .main-header {
        background-color: #1f77b4;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados das planilhas de referência
@st.cache_data
def load_reference_data():
    """Carrega dados das planilhas de referência"""
    try:
        # Carregar dados de materiais (Planilha3)
        materiais_df = pd.read_excel('data/Controle-Copia(9).xlsx', sheet_name='Planilha3')
        # Carregar dados de compatibilidade
        compatibilidade_df = pd.read_excel('data/Controle-Copia(9).xlsx', sheet_name='Compatibilidade')
        # Carregar dados de locais (Planilha1)
        try:
            locais_df = pd.read_excel('data/Controle-Copia(9).xlsx', sheet_name='Planilha1')
        except:
            # Se Planilha1 não existir, usar dados padrão
            locais_df = pd.DataFrame({'Onde': ['Área 1', 'Área 2', 'Área 3', 'Estoque A', 'Estoque B']})
        return materiais_df, compatibilidade_df, locais_df
    except Exception as e:
        st.error(f"Erro ao carregar dados de referência: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Função para carregar dados de recebimento
def load_recebimento_data():
    """Carrega dados existentes de recebimento"""
    if os.path.exists('data/recebimento.csv'):
        return pd.read_csv('data/recebimento.csv')
    else:
        # Criar DataFrame vazio com as colunas necessárias
        columns = [
            'teste', '04 - Item Material na NF', '02 - Nf', '05 - RR', '6 - RR',
            '06 - Chave de acesso', '07 - Fornecedor', '10 - Qtd', '09 - Descrição Material',
            '11 - Tipo', '08 - Ni', '17 - Área', '12 - Medida Pallets', '13 - Programado',
            '15 - Recebedor', '14 - Status', '16 - Observação', '01 - Nº Processo',
            'Controle', 'Data', 'Dia', 'Mês', 'Ano', '__PowerAppsId__'
        ]
        return pd.DataFrame(columns=columns)

# Função para salvar dados de recebimento
def save_recebimento_data(df):
    """Salva dados de recebimento"""
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/recebimento.csv', index=False)

# Função para buscar descrição do material
def get_material_description(ni, materiais_df):
    """Busca descrição do material baseado no NI"""
    if not materiais_df.empty and ni:
        # Assumindo que a primeira coluna contém o NI e a segunda a descrição
        material = materiais_df[materiais_df.iloc[:, 0].astype(str) == str(ni)]
        if not material.empty:
            return material.iloc[0, 1]  # Segunda coluna (descrição)
    return ""

# Função para buscar compatibilidade
def get_compatibility_info(ni, compatibilidade_df):
    """Busca informações de compatibilidade baseado no NI"""
    if not compatibilidade_df.empty and ni:
        compatibility = compatibilidade_df[compatibilidade_df['NI'].astype(str) == str(ni)]
        if not compatibility.empty:
            return compatibility.iloc[0]['Materiais Incompatíveis'] if 'Materiais Incompatíveis' in compatibility.columns else ""
    return ""

# Carregar dados de referência
materiais_df, compatibilidade_df, locais_df = load_reference_data()

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🏭 Sistema de Recebimento - Suzano</h1>
    <p>Cadastro de Materiais Recebidos</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegação
st.sidebar.title("📋 Menu")
page = st.sidebar.selectbox("Selecione uma opção:", ["Cadastro", "Visualizar Dados", "Gerar Rótulo"])

if page == "Cadastro":
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    # Formulário de cadastro
    with st.form("recebimento_form"):
        st.subheader("📝 Formulário de Recebimento")
        col1, col2, col3 = st.columns(3)
        with col1:
            # Campos de data
            data_recebimento = st.date_input("Data", value=datetime.date.today())
            dia = data_recebimento.day
            mes = data_recebimento.month
            ano = data_recebimento.year
            # Campos básicos
            num_processo = st.text_input("01 - Nº Processo")
            nf = st.text_input("02 - NF")
            item_nf = st.text_input("03 - Item NF")
        with col2:
            item_material_nf = st.text_input("04 - Item Material na NF")
            rr = st.text_input("05 - RR")
            rr2 = st.text_input("06 - RR")
            chave_acesso = st.text_input("07 - Chave de Acesso")
        with col3:
            fornecedor = st.text_input("08 - Fornecedor")
            ni = st.text_input("09 - NI (Número de Identificação)")
            qtd = st.number_input("10 - Quantidade", min_value=0.0, step=0.1)
        # Buscar descrição automaticamente baseada no NI
        descricao_material = ""
        if ni:
            descricao_material = get_material_description(ni, materiais_df)
        col4, col5 = st.columns(2)
        with col4:
            descricao_material_input = st.text_input("11 - Descrição Material", value=descricao_material)
            tipo = st.text_input("12 - Tipo")
            medida_pallets = st.text_input("13 - Medida Pallets")
            programado = st.text_input("14 - Programado")
        with col5:
            recebedor = st.text_input("15 - Recebedor")
            status = st.selectbox("16 - Status", ["", "Recebido", "Pendente", "Em Análise"])
            # Lista suspensa para área (baseada nos locais disponíveis)
            areas_disponiveis = [""] + list(locais_df['Onde'].dropna().unique()) if not locais_df.empty else ["Área 1", "Área 2", "Área 3"]
            area = st.selectbox("17 - Área", areas_disponiveis)
            observacao = st.text_area("16 - Observação")
        # Campos automáticos
        controle = st.text_input("Controle", value=str(uuid.uuid4())[:8])
        teste = st.selectbox("Teste", ["Outro Período", "Período Atual"])
        # Botão de envio
        submitted = st.form_submit_button("📤 Enviar", use_container_width=True)
        if submitted:
            # Validações básicas
            if not num_processo or not nf or not ni:
                st.error("⚠️ Por favor, preencha os campos obrigatórios: Nº Processo, NF e NI")
            else:
                # Criar novo registro
                novo_registro = {
                    'teste': teste,
                    '04 - Item Material na NF': item_material_nf,
                    '02 - Nf': nf,
                    '05 - RR': rr,
                    '6 - RR': rr2,
                    '06 - Chave de acesso': chave_acesso,
                    '07 - Fornecedor': fornecedor,
                    '10 - Qtd': qtd,
                    '09 - Descrição Material': descricao_material_input,
                    '11 - Tipo': tipo,
                    '08 - Ni': ni,
                    '17 - Área': area,
                    '12 - Medida Pallets': medida_pallets,
                    '13 - Programado': programado,
                    '15 - Recebedor': recebedor,
                    '14 - Status': status,
                    '16 - Observação': observacao,
                    '01 - Nº Processo': num_processo,
                    'Controle': controle,
                    'Data': data_recebimento.strftime('%Y-%m-%d'),
                    'Dia': dia,
                    'Mês': mes,
                    'Ano': ano,
                    '__PowerAppsId__': str(uuid.uuid4())
                }
                # Carregar dados existentes e adicionar novo registro
                df_recebimento = load_recebimento_data()
                df_recebimento = pd.concat([df_recebimento, pd.DataFrame([novo_registro])], ignore_index=True)
                # Salvar dados
                save_recebimento_data(df_recebimento)
                st.markdown("""
                <div class="success-message">
                    ✅ <strong>Sucesso!</strong> Material recebido e cadastrado com sucesso!
                </div>
                """, unsafe_allow_html=True)
                # Limpar formulário (rerun)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Visualizar Dados":
    st.subheader("📊 Dados de Recebimento")
    df_recebimento = load_recebimento_data()
    if not df_recebimento.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_fornecedor = st.selectbox("Filtrar por Fornecedor:", ["Todos"] + list(df_recebimento['07 - Fornecedor'].dropna().unique()))
        with col2:
            filtro_status = st.selectbox("Filtrar por Status:", ["Todos"] + list(df_recebimento['14 - Status'].dropna().unique()))
        with col3:
            filtro_area = st.selectbox("Filtrar por Área:", ["Todos"] + list(df_recebimento['17 - Área'].dropna().unique()))
        # Aplicar filtros
        df_filtrado = df_recebimento.copy()
        if filtro_fornecedor != "Todos":
            df_filtrado = df_recebimento[df_recebimento['07 - Fornecedor'] == filtro_fornecedor]
        if filtro_status != "Todos":
            df_filtrado = df_recebimento[df_recebimento['14 - Status'] == filtro_status]
        if filtro_area != "Todos":
            df_filtrado = df_recebimento[df_recebimento['17 - Área'] == filtro_area]
        # Exibir dados
        st.dataframe(df_filtrado, use_container_width=True)
        # Estatísticas
        st.subheader("📈 Estatísticas")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Registros", len(df_filtrado))
        with col2:
            st.metric("Quantidade Total", df_filtrado['10 - Qtd'].sum())
        with col3:
            st.metric("Fornecedores Únicos", df_filtrado['07 - Fornecedor'].nunique())
        with col4:
            st.metric("Áreas Utilizadas", df_filtrado['17 - Área'].nunique())
    else:
        st.info("📝 Nenhum dado de recebimento encontrado. Cadastre o primeiro material!")

elif page == "Gerar Rótulo":
    st.subheader("🏷️ Gerador de Rótulos")
    df_recebimento = load_recebimento_data()
    if not df_recebimento.empty:
        # Seleção do item para gerar rótulo
        ni_selecionado = st.selectbox("Selecione o NI para gerar rótulo:", 
                                     [""] + list(df_recebimento['08 - Ni'].dropna().unique()))
        if ni_selecionado:
            # Buscar informações do item
            item = df_recebimento[df_recebimento['08 - Ni'] == ni_selecionado].iloc[-1]  # Último registro
            # Buscar descrição e compatibilidade
            descricao = get_material_description(ni_selecionado, materiais_df)
            compatibilidade = get_compatibility_info(ni_selecionado, compatibilidade_df)
            # Exibir rótulo
            st.markdown("---")
            st.markdown("### 🏷️ Rótulo Gerado")
            rotulo_html = f"""
            <div style="border: 2px solid #000; padding: 20px; margin: 20px 0; background-color: white;">
                <h3 style="text-align: center; margin-bottom: 20px;">RÓTULO DE MATERIAL</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">NI:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{ni_selecionado}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">Descrição:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{descricao or item['09 - Descrição Material']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">Fornecedor:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{item['07 - Fornecedor']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">Quantidade:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{item['10 - Qtd']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">Área:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{item['17 - Área']}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 8px; font-weight: bold;">Data:</td>
                        <td style="border: 1px solid #000; padding: 8px;">{item['Data']}</td>
                    </tr>
                    {f'<tr><td style="border: 1px solid #000; padding: 8px; font-weight: bold; color: red;">Incompatibilidade:</td><td style="border: 1px solid #000; padding: 8px; color: red;">{compatibilidade}</td></tr>' if compatibilidade else ''}
                </table>
            </div>
            """
            st.markdown(rotulo_html, unsafe_allow_html=True)
            # Botão para imprimir (simulado)
            if st.button("🖨️ Imprimir Rótulo"):
                st.success("✅ Rótulo enviado para impressão!")
    else:
        st.info("📝 Nenhum material cadastrado para gerar rótulo.")

# Footer
st.markdown("---")
st.markdown("**Sistema de Recebimento Suzano** - Desenvolvido com Streamlit")
