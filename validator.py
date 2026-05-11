import re


def horario_valido(horario):
    return bool(re.match(r"^\d{2}:\d{2}$", str(horario).strip()))


def normalizar_marcacoes(marcacoes):
    limpas = []

    for h in marcacoes:
        h = str(h).strip()

        if not h:
            continue

        h = h.replace("h", ":").replace("H", ":")

        if re.match(r"^\d{1}:\d{2}$", h):
            h = "0" + h

        if horario_valido(h):
            limpas.append(h)

    return sorted(list(dict.fromkeys(limpas)))


def validar_dados(dados):
    resultado = []

    for item in dados:
        data = item.get("data", "").strip()
        marcacoes = normalizar_marcacoes(item.get("marcacoes", []))

        alerta = ""

        if len(marcacoes) % 2 != 0:
            alerta = "Marcação ímpar"

        if len(marcacoes) > 4:
            alerta = "Mais de 4 marcações no dia"

        resultado.append({
            "Data": data,
            "Entrada 1": marcacoes[0] if len(marcacoes) > 0 else "",
            "Saída 1": marcacoes[1] if len(marcacoes) > 1 else "",
            "Entrada 2": marcacoes[2] if len(marcacoes) > 2 else "",
            "Saída 2": marcacoes[3] if len(marcacoes) > 3 else "",
            "Alerta": alerta
        })

    return resultado
