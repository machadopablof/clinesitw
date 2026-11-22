"""
AgriCad - tela de login escrita em Python.

Roda direto no navegador com PyScript (Pyodide), por isso funciona no
GitHub Pages, que só hospeda arquivos estáticos.

Modo demonstração: usuários e senhas ficam salvos apenas no navegador
(localStorage). Não use senhas reais.
"""

import hashlib
import html
import json
import secrets

from pyodide.ffi import create_proxy
from pyscript import document, window

USERS_KEY = "agricad_users"
SESSION_KEY = "agricad_session"

EYE = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7'
    '-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>'
)
EYE_OFF = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 '
    '12 19c-6.5 0-10-7-10-7a18.5 18.5 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c6.5 0 '
    '10 7 10 7a18.5 18.5 0 0 1-2.16 3.19M14.12 14.12a3 3 0 1 1-4.24-4.24"/>'
    '<line x1="2" y1="2" x2="22" y2="22"/></svg>'
)


# --------------------------------------------------------------------------
# Armazenamento (localStorage / sessionStorage do navegador)
# --------------------------------------------------------------------------
def storage_get(store, key, default):
    try:
        raw = store.getItem(key)
        return json.loads(raw) if raw else default
    except Exception:
        return default


def storage_set(store, key, value):
    try:
        store.setItem(key, json.dumps(value))
    except Exception:
        pass


def load_users():
    return storage_get(window.localStorage, USERS_KEY, {})


def save_users(users):
    storage_set(window.localStorage, USERS_KEY, users)


def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def create_user(name, email, password):
    salt = secrets.token_hex(8)
    return {"name": name, "salt": salt, "hash": hash_password(password, salt)}


def check_password(user, password):
    return secrets.compare_digest(user["hash"], hash_password(password, user["salt"]))


def current_session():
    return storage_get(window.localStorage, SESSION_KEY, None) or storage_get(
        window.sessionStorage, SESSION_KEY, None
    )


def start_session(email, remember):
    store = window.localStorage if remember else window.sessionStorage
    storage_set(store, SESSION_KEY, {"email": email})


def end_session():
    for store in (window.localStorage, window.sessionStorage):
        try:
            store.removeItem(SESSION_KEY)
        except Exception:
            pass


# --------------------------------------------------------------------------
# Componentes de HTML
# --------------------------------------------------------------------------
def esc(text):
    return html.escape(str(text or ""), quote=True)


def brand_mobile():
    return (
        '<div class="brand brand-mobile">'
        '<img src="assets/logo.svg" alt="AgriCad" /><span>AgriCad</span></div>'
    )


def demo_notice():
    return (
        '<div class="notice" role="note"><strong>Modo demonstração</strong>'
        "<p>Usuários, senhas e dados ficam apenas neste navegador e podem ser "
        "alterados por quem usa o aparelho. Não use senhas reais nem dados sensíveis.</p></div>"
    )


def alert(message, kind="error"):
    if not message:
        return ""
    role = "alert" if kind == "error" else "status"
    return f'<div class="alert {kind}" role="{role}">{esc(message)}</div>'


def field(label, name, kind="text", value="", autocomplete="", password=False):
    input_html = (
        f'<input id="{name}" name="{name}" type="{kind}" value="{esc(value)}" '
        f'autocomplete="{autocomplete}" required />'
    )
    if password:
        input_html = (
            f'<div class="pw-row">{input_html}'
            f'<button type="button" class="icon-btn" data-action="toggle-pw" data-target="{name}" '
            f'aria-label="Mostrar senha">{EYE}</button></div>'
        )
    return f'<div class="field"><label for="{name}">{label}</label>{input_html}</div>'


# --------------------------------------------------------------------------
# Telas
# --------------------------------------------------------------------------
def view_login(message="", kind="error", email=""):
    return (
        brand_mobile()
        + "<h1>Bem-vindo ao AgriCad</h1>"
        + '<p class="subtitle">Entre com sua conta para continuar.</p>'
        + demo_notice()
        + alert(message, kind)
        + '<form data-form="login" novalidate>'
        + field("E-mail", "email", "email", email, "email")
        + field("Senha", "password", "password", "", "current-password", password=True)
        + '<div class="row-between">'
        + '<label class="check"><input type="checkbox" name="remember" /> Lembrar de mim</label>'
        + '<button type="button" class="link" data-action="go-forgot">Esqueci minha senha</button>'
        + "</div>"
        + '<button type="submit" class="btn">Entrar</button>'
        + "</form>"
        + '<p class="footer-text">Ainda não tem conta? '
        + '<a href="#" class="link strong" data-action="go-register">Criar minha conta</a></p>'
    )


def view_register(message=""):
    return (
        brand_mobile()
        + "<h1>Criar minha conta</h1>"
        + '<p class="subtitle">Preencha os dados para começar a usar o AgriCad.</p>'
        + demo_notice()
        + alert(message)
        + '<form data-form="register" novalidate>'
        + field("Nome", "name", "text", "", "name")
        + field("E-mail", "email", "email", "", "email")
        + field("Senha", "password", "password", "", "new-password", password=True)
        + field("Confirmar senha", "confirm", "password", "", "new-password", password=True)
        + '<button type="submit" class="btn">Criar conta</button>'
        + "</form>"
        + '<p class="footer-text">Já tem conta? '
        + '<a href="#" class="link strong" data-action="go-login">Entrar</a></p>'
    )


def view_forgot(message=""):
    return (
        brand_mobile()
        + "<h1>Redefinir senha</h1>"
        + '<p class="subtitle">No modo demonstração você pode definir uma nova senha direto aqui.</p>'
        + alert(message)
        + '<form data-form="forgot" novalidate>'
        + field("E-mail", "email", "email", "", "email")
        + field("Nova senha", "password", "password", "", "new-password", password=True)
        + '<button type="submit" class="btn">Salvar nova senha</button>'
        + "</form>"
        + '<p class="footer-text">'
        + '<a href="#" class="link strong" data-action="go-login">Voltar para o login</a></p>'
    )


def view_dashboard(user):
    first_name = esc(user["name"].split(" ")[0]) if user.get("name") else "produtor"
    cards = [
        ("Safras ativas", "0"),
        ("Despesas do mês", "R$ 0,00"),
        ("Insumos em estoque", "0"),
        ("Rentabilidade", "0%"),
    ]
    cards_html = "".join(
        f'<div class="dash-card"><span>{label}</span><b>{value}</b></div>'
        for label, value in cards
    )
    return (
        brand_mobile()
        + f"<h1>Olá, {first_name}!</h1>"
        + '<p class="subtitle">Você entrou no AgriCad. Este é o seu painel.</p>'
        + f'<div class="dash-cards">{cards_html}</div>'
        + '<form><button type="button" class="btn outline" data-action="logout">Sair</button></form>'
    )


# --------------------------------------------------------------------------
# Lógica
# --------------------------------------------------------------------------
view = document.getElementById("view")


def render(content):
    view.innerHTML = content
    first = view.querySelector("input")
    if first:
        first.focus()


def form_values(form):
    data = {}
    for el in form.querySelectorAll("input"):
        if el.type == "checkbox":
            data[el.name] = bool(el.checked)
        else:
            data[el.name] = str(el.value).strip()
    return data


def valid_email(email):
    if "@" not in email:
        return False
    local, _, domain = email.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".")


def handle_login(data):
    email = data.get("email", "").lower()
    password = data.get("password", "")
    if not email or not password:
        return render(view_login("Informe e-mail e senha.", email=email))
    user = load_users().get(email)
    if not user or not check_password(user, password):
        return render(view_login("E-mail ou senha incorretos.", email=email))
    start_session(email, data.get("remember", False))
    render(view_dashboard(user))


def handle_register(data):
    name = data.get("name", "")
    email = data.get("email", "").lower()
    password = data.get("password", "")
    if not name:
        return render(view_register("Informe seu nome."))
    if not valid_email(email):
        return render(view_register("Informe um e-mail válido."))
    if len(password) < 6:
        return render(view_register("A senha precisa ter pelo menos 6 caracteres."))
    if password != data.get("confirm", ""):
        return render(view_register("As senhas não conferem."))
    users = load_users()
    if email in users:
        return render(view_register("Já existe uma conta com este e-mail."))
    users[email] = create_user(name, email, password)
    save_users(users)
    render(view_login("Conta criada! Agora é só entrar.", kind="ok", email=email))


def handle_forgot(data):
    email = data.get("email", "").lower()
    password = data.get("password", "")
    users = load_users()
    if email not in users:
        return render(view_forgot("Não encontramos uma conta com este e-mail."))
    if len(password) < 6:
        return render(view_forgot("A senha precisa ter pelo menos 6 caracteres."))
    users[email] = create_user(users[email]["name"], email, password)
    save_users(users)
    render(view_login("Senha alterada com sucesso.", kind="ok", email=email))


FORMS = {"login": handle_login, "register": handle_register, "forgot": handle_forgot}


def on_submit(event):
    form = event.target
    handler = FORMS.get(form.getAttribute("data-form"))
    if handler:
        event.preventDefault()
        handler(form_values(form))


def on_click(event):
    target = event.target.closest("[data-action]")
    if not target:
        return
    action = target.getAttribute("data-action")
    event.preventDefault()
    if action == "toggle-pw":
        field_el = document.getElementById(target.getAttribute("data-target"))
        showing = field_el.type == "text"
        field_el.type = "password" if showing else "text"
        target.innerHTML = EYE if showing else EYE_OFF
        target.setAttribute("aria-label", "Mostrar senha" if showing else "Ocultar senha")
    elif action == "go-register":
        render(view_register())
    elif action == "go-forgot":
        render(view_forgot())
    elif action == "go-login":
        render(view_login())
    elif action == "logout":
        end_session()
        render(view_login("Você saiu da sua conta.", kind="ok"))


def start():
    view.addEventListener("submit", create_proxy(on_submit))
    view.addEventListener("click", create_proxy(on_click))

    session = current_session()
    user = load_users().get(session["email"]) if session else None
    if user:
        view.innerHTML = view_dashboard(user)
    else:
        view.innerHTML = view_login()

    document.getElementById("boot").remove()
    document.getElementById("app").hidden = False


start()
