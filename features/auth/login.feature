# language: pt
Funcionalidade:

  Cenário: Autenticação/Mobile - Validar login com credenciais válidas
    Dado que o usuário está na tela de login do aplicativo em "Autenticação/Mobile" com um cadastro ativo
    Quando informa o e-mail cadastrado com a senha correspondente
    E toca no botão "Entrar"
    Então o sistema exibe a tela inicial do aplicativo

  Cenário: Autenticação/Mobile - Validar bloqueio do login com senha incorreta
    Dado que o usuário está na tela de login do aplicativo em "Autenticação/Mobile" com um cadastro ativo
    Quando informa o e-mail cadastrado com uma senha diferente da cadastrada
    E toca no botão "Entrar"
    Então o sistema exibe a mensagem "E-mail ou senha inválidos"
    Mas mantém o usuário na tela de login
