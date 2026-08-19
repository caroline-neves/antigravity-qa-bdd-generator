# Issue do Jira: PROJ-502 - Autenticação por Biometria no App Mobile

## Informações Gerais
- **Chave da Issue**: PROJ-502
- **Título**: Adicionar Autenticação por Biometria (FaceID / Digital) no Login
- **Módulo**: Autenticação / Mobile

## Descrição & Regras de Negócio
Como usuário do aplicativo mobile, quero poder habilitar e utilizar a autenticação biométrica (Touch ID / Face ID) para realizar o login rapidamente sem precisar digitar a senha a cada acesso.

## Critérios de Aceite
1. O aplicativo deve permitir habilitar ou desabilitar o login por biometria nas configurações de segurança do perfil.
2. Ao abrir o aplicativo com a biometria ativada, a solicitação de biometria nativa do sistema deve ser exibida automaticamente.
3. Se a leitura biométrica for bem-sucedida, o usuário deve ser autenticado e direcionado para a tela inicial.
4. Se o usuário falhar na biometria por 3 vezes consecutivas, o sistema deve exigir a senha alfanumérica tradicional.
5. Em dispositivos sem suporte a hardware biométrico, a opção de login por biometria deve permanecer desabilitada e oculta.
