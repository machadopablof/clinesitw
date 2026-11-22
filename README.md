# clinesite — AgriCad em Python

Tela de login do **AgriCad** (gestão agrícola) feita em **Python**, rodando direto
no navegador com [PyScript](https://pyscript.net). Por isso funciona no
**GitHub Pages**, que só hospeda arquivos estáticos.

## Arquivos

| Arquivo | O que faz |
|---|---|
| `main.py` | Toda a lógica em Python: login, cadastro, redefinir senha, "lembrar de mim", painel e sair |
| `index.html` | Estrutura da página (tela dividida: imagem à esquerda, formulário à direita) |
| `style.css` | Visual (fonte Manrope, verde `#2f7f33`, modo escuro automático) |
| `pyscript.toml` | Configuração do PyScript |
| `assets/logo.svg` | Logo |
| `.github/workflows/pages.yml` | Publica o site automaticamente no GitHub Pages |

## Modo demonstração

As contas ficam salvas só no navegador (`localStorage`), com a senha guardada como
hash SHA-256 com salt. Não use senhas reais: não existe servidor.

## Publicar no GitHub Pages

1. No GitHub, abra **Settings → Pages** e, em **Source**, escolha **GitHub Actions**.
2. Envie o código para a branch `main`. O workflow publica sozinho.
3. O site fica em `https://<seu-usuario>.github.io/clinesitw/`.

## Rodar no seu computador

```bash
python -m http.server 8000
```

Depois abra http://localhost:8000.
