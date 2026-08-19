@PROJ-TC-101
Scenario: Autenticação/Mobile - Login bem-sucedido com credenciais válidas [Declarativo]
  Given que o usuário está na tela inicial de login em "Autenticação/Mobile"
  When insere o e-mail "usuario@exemplo.com", a senha "Senha123"
  And toca no botão "Entrar"
  Then o login é realizado com sucesso
  And a tela inicial do usuário é exibida

@PROJ-TC-102
Scenario: Autenticação/Mobile - Tentativa de login com senha incorreta [Declarativo]
  Given que o usuário está na tela inicial de login em "Autenticação/Mobile"
  When insere o e-mail "usuario@exemplo.com", a senha "SenhaErrada"
  And toca no botão "Entrar"
  Then o sistema exibe a mensagem "E-mail ou senha inválidos"
  And a sessão não é iniciada
