# 🎮 OmniOverlay

**OmniOverlay** é uma aplicação desktop moderna desenvolvida em Python com **CustomTkinter**, projetada para funcionar como um painel flutuante (overlay) completo. Ela oferece gerenciamento de perfis, atalhos customizados inteligentes, monitoramento de hardware em tempo real, assistente de IA integrada, player de vídeo e personalização visual avançada.

---

## ✨ Funcionalidades Principais

* **🔄 Gerenciamento de Perfis (Multi-contas):** Crie, altere, exclua e personalize diferentes perfis de usuário com avatares e configurações independentes salvas automaticamente.
* **⚡ Atalho Global (`Alt + Z`):** Abra ou oculte o overlay instantaneamente de qualquer lugar, mesmo com jogos ou aplicações em tela cheia (`pynput`).
* **📊 Monitoramento de Hardware:** Acompanhe o uso de CPU e Memória RAM em tempo real tanto no cabeçalho quanto em um painel detalhado nas configurações (`psutil`).
* **🚀 Hub de Atalhos & Busca Universal:** Acesso rápido a links web (`.com`, `http`), aplicativos do sistema (`.exe`, `explorer.exe`, `taskmgr.exe`) ou atalhos personalizados organizados em categorias com suporte a ícones customizados.
* **🤖 OmniAI (Assistente Inteligente):** Chat integrado para responder dúvidas, sugerir aplicativos e auxiliar na rotina do usuário.
* **🎬 Player de Vídeo & Modo Cinema:** Reproduza vídeos diretamente na aplicação (`.mp4`, `.avi`, etc.) e utilize o modo tela cheia imersivo.
* **🎨 Aparência e Temas Dinâmicos:** Alternância entre modo Claro/Escuro e paletas de cores de destaque customizadas (Azul, Vermelho, Verde e Roxo) com suporte a imagens de fundo personalizadas.

---

## 🛠️ Tecnologias Utilizadas
z
* **Python 3.x**
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** (Interface gráfica moderna)
* **Pillow (PIL)** (Manipulação de imagens e avatares)
* **psutil** (Monitoramento de recursos do sistema)
* **pynput** (Captura de atalhos globais de teclado)
* **tkvideoplayer** (Reprodução de mídia integrada)

---

## 📦 Instalação e Execução

Siga os passos abaixo para configurar o ambiente e rodar o projeto:

### 1. Clonar ou baixar o repositório
```bash
git clone [https://github.com/seu-usuario/omni-overlay.git](https://github.com/seu-usuario/omni-overlay.git)
cd omni-overlay