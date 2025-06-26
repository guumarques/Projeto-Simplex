import streamlit as st #monta interface web interativa
import pandas as pd #cria e organiza os dados em forma de tabela
from functions import create_simplex_table, simplex_optimization

def main():
    st.image("logo.jpg", width=400)
    st.title("SolveX - Solucionador de Programação Linear com Método Simplex")

    num_vars = st.number_input("Número de Variáveis (Colunas)", min_value=1, max_value=5, step=1)
    num_constraints = st.number_input("Número de Restrições (Linhas)", min_value=1, max_value=5, step=1)
    optimization_type = st.radio("Tipo de Otimização", ["Maximizar", "Minimizar"])
    table_created = False

    if st.button("Criar Tabela Simplex"):
        st.session_state['initial_simplex'] = create_simplex_table(num_vars, num_constraints, optimization_type)

    if 'initial_simplex' in st.session_state:
        st.write("Preencha a tabela abaixo:")
        st.session_state['updated_simplex'] = st.data_editor(st.session_state['initial_simplex'])
        table_created = True

    if table_created:
        if st.button("Resolver Tableau"):
            solution, optimal_value, shadow_prices, slacks, deltas = simplex_optimization(
                st.session_state['updated_simplex'],
                optimization_type
            )

            # Salva no estado para reutilizar depois
            st.session_state['solucao_base'] = {
                'solution': solution,
                'optimal_value': optimal_value,
                'shadow_prices': shadow_prices,
                'slacks': slacks,
                'deltas': deltas,
                'num_constraints': num_constraints
            }

            # Exibir todos os resultados normalmente
            st.subheader("Solução do Problema")
            st.subheader("Valor Ótimo da Função Objetivo (Z):")
            st.write(optimal_value)

            st.subheader("Valores Ótimos das Variáveis de Decisão")
            solution_df = pd.DataFrame(list(solution.items()), columns=['Variável', 'Valor'])
            st.table(solution_df)

            st.subheader("Preços Sombra das Restrições")
            shadow_prices_df = pd.DataFrame(list(shadow_prices.items()), columns=['Restrição', 'Preço Sombra'])
            st.table(shadow_prices_df)

            st.subheader("Folgas das Restrições")
            slacks_df = pd.DataFrame(list(slacks.items()), columns=['Restrição', 'Folga'])
            st.table(slacks_df)

            st.subheader("Deltas (Lucros Relativos)")
            if deltas:
                deltas_df = pd.DataFrame(list(deltas.items()), columns=['Variável', 'Delta'])
                st.table(deltas_df)
            else:
                st.warning("Não foi possível calcular os deltas.")

    # --- Seção para simulação com alteração nas restrições ---
    if 'solucao_base' in st.session_state:
        st.markdown("---")
        st.subheader("Simulação: Alterar lado direito das restrições (usando preços sombra)")

        st.markdown(
            "Insira o valor do aumento (positivo) ou redução (negativo) para cada restrição. "
            "O sistema calculará o novo lucro estimado com base nos preços sombra, sem resolver novamente."
        )

        shadow_prices = st.session_state['solucao_base']['shadow_prices']
        valor_otimo_original = st.session_state['solucao_base']['optimal_value']
        num_constraints = st.session_state['solucao_base']['num_constraints']
        nomes_reais = list(shadow_prices.keys())

        alteracoes = []
        for i in range(num_constraints):
            nome = nomes_reais[i] if i < len(nomes_reais) else f"Restrição {i+1}"
            delta = st.number_input(f"Alterar {nome} (Δ unidades):", value=0.0, key=f"mod_{i}")
            alteracoes.append((nome, delta))

        if st.button("Calcular novo lucro estimado"):
            novo_lucro_estimado = valor_otimo_original

            st.markdown("#### Detalhes da simulação:")
            for nome, delta in alteracoes:
                preco = shadow_prices.get(nome, 0.0)
                st.write(f"{nome}: preço sombra = {preco}, Δ = {delta}")
                novo_lucro_estimado += preco * delta

            st.markdown(f"### 💰 Novo lucro estimado: R$ {novo_lucro_estimado:.2f}")
            st.markdown(f"Lucro original: R$ {valor_otimo_original:.2f}")
            diff = novo_lucro_estimado - valor_otimo_original
            st.markdown(f"Variação estimada: **{'+' if diff >= 0 else ''}{diff:.2f}**")

            if diff >= 0:
                st.success("A alteração pode aumentar ou manter o lucro.")
            else:
                st.warning("A alteração pode reduzir o lucro.")

if __name__ == '__main__':
    main()
