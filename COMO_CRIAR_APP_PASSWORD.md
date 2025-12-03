# Como Criar App Password do Gmail - Passo a Passo

## ✅ Você NÃO precisa criar um email novo!
Use seu email atual: `baute.thomas25@gmail.com`

## O que é App Password?
É uma senha especial que o Gmail gera para permitir que aplicativos externos (como nosso sistema) enviem emails usando sua conta, sem precisar da sua senha normal.

---

## 📋 Passo a Passo Detalhado

### Passo 1: Verificar se tem Verificação em Duas Etapas Ativada

1. Acesse: https://myaccount.google.com/security
2. Procure por "Verificação em duas etapas"
3. Se estiver **desativada**, você precisa ativar primeiro:
   - Clique em "Verificação em duas etapas"
   - Siga as instruções para ativar
   - Isso é necessário para criar App Passwords

### Passo 2: Criar a App Password

1. Acesse: https://myaccount.google.com/apppasswords
   - Se não conseguir acessar diretamente, vá em:
   - https://myaccount.google.com/security
   - Role até "Como fazer login no Google"
   - Clique em "Senhas de app"

2. Você verá uma tela pedindo:
   - **Selecione o app**: Escolha "Email"
   - **Selecione o dispositivo**: Escolha "Outro (nome personalizado)"
   - **Digite um nome**: Ex: "Inventory Anomaly Detector"
   - Clique em **"Gerar"**

3. Uma senha de 16 caracteres será gerada, algo como:
   ```
   abcd efgh ijkl mnop
   ```
   ⚠️ **IMPORTANTE**: Copie essa senha AGORA! Você não conseguirá vê-la novamente.

4. A senha terá espaços, mas você pode copiar e colar normalmente - o sistema vai remover os espaços automaticamente.

### Passo 3: Configurar no Projeto

1. Abra o arquivo `src/config.py`

2. Encontre a seção `EMAIL_CONFIG`:

```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_username": "baute.thomas25@gmail.com",
    "smtp_password": None,  # <-- AQUI você vai colar a senha
    "from_email": "baute.thomas25@gmail.com",
    "to_emails": ["baute.thomas25@gmail.com"],
    "use_tls": True,
}
```

3. Substitua `None` pela senha que você copiou:

```python
"smtp_password": "abcdefghijklmnop",  # Cole a senha aqui (sem espaços)
```

4. Salve o arquivo

### Passo 4: Testar

Execute:
```bash
py test_alerts.py
```

Ou teste diretamente:
```python
from src.alerts import send_email_alert

send_email_alert(
    subject="Teste de Email",
    message="Este é um teste de envio de email do sistema de anomalias."
)
```

---

## 🔒 Segurança

- ✅ A App Password é mais segura que usar sua senha normal
- ✅ Você pode revogar a App Password a qualquer momento
- ✅ Se perder a senha, basta criar uma nova
- ⚠️ **NUNCA** compartilhe sua App Password
- ⚠️ **NUNCA** commite a senha no Git (já está no .gitignore)

---

## ❓ Dúvidas Frequentes

**P: Preciso criar um email novo?**
R: NÃO! Use seu email atual.

**P: Posso usar minha senha normal?**
R: NÃO! O Gmail não permite. Você DEVE usar App Password.

**P: A App Password funciona para sempre?**
R: Sim, até você revogá-la manualmente.

**P: Posso usar a mesma App Password em vários projetos?**
R: Sim, mas é mais seguro criar uma App Password por projeto.

**P: E se eu perder a App Password?**
R: Não tem problema! Crie uma nova e atualize no código.

---

## 📸 Exemplo Visual

```
┌─────────────────────────────────────┐
│  Senhas de app                      │
├─────────────────────────────────────┤
│                                     │
│  Selecione o app:                   │
│  [Email ▼]                          │
│                                     │
│  Selecione o dispositivo:          │
│  [Outro (nome personalizado) ▼]    │
│                                     │
│  Nome:                              │
│  [Inventory Anomaly Detector]      │
│                                     │
│  [Gerar]                            │
│                                     │
└─────────────────────────────────────┘

Após clicar em "Gerar":

┌─────────────────────────────────────┐
│  Sua senha de app foi gerada        │
├─────────────────────────────────────┤
│                                     │
│  abcd efgh ijkl mnop                │
│                                     │
│  [Copiar] [Fechar]                  │
│                                     │
└─────────────────────────────────────┘
```

---

## ✅ Checklist

- [ ] Verificação em duas etapas ativada
- [ ] App Password criada
- [ ] Senha copiada
- [ ] Senha adicionada em `src/config.py`
- [ ] Teste executado com sucesso

---

**Pronto! Agora você pode enviar emails do sistema usando sua conta Gmail!** 🎉

