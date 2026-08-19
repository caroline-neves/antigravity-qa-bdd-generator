@PROJ-TC-101
Scenario: Autenticação/Mobile - Layout do modal de login [Procedural]
  Given que o usuário esteja no submódulo "Login" do módulo "Autenticação"
  When visualiza a tela inicial
  Then o sistema exibe os campos obrigatórios "E-mail", "Senha"
  And exibe os botões:
    * "Entrar", "Esqueci minha senha", "Entrar com Biometria"
