Scenario: Autenticação/Mobile - Login efetuado com sucesso via biometria válida [Declarativo]
  Given que a funcionalidade de biometria está ativada no perfil em "Autenticação/Mobile"
  When abre o aplicativo
  And realiza a confirmação biométrica válida
  Then a autenticação é realizada com sucesso
  And a tela inicial do usuário é exibida

Scenario: Autenticação/Mobile - Exigência de senha tradicional após 3 tentativas biométricas incorretas [Declarativo]
  Given que a biometria está ativada em "Autenticação/Mobile"
  When o usuário falha na leitura biométrica por 3 vezes consecutivas
  Then o sistema bloqueia temporariamente a autenticação biométrica
  And exige a senha alfanumérica tradicional para realizar o login
