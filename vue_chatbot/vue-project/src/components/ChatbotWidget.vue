<template>
    <div class="chatbot-widget" :class="{ 'chatbot-widget--open': isChatOpen }">
      <button v-if="!isChatOpen" @click="openChat" class="chatbot-widget__toggle">
        Need help?
      </button>
      <div v-else class="chatbot-widget__container">
        <div class="chatbot-widget__header">
          <h3>Chat Support</h3>
          <button @click="closeChat" class="chatbot-widget__close">&times;</button>
        </div>
        <div class="chatbot-widget__messages" ref="messageContainer">
          <div v-for="(message, index) in messages" :key="index" class="chatbot-widget__message" :class="message.from">
            <div v-html="formatMessage(message.text)"></div>
          </div>
          <div v-if="isTyping" class="chatbot-widget__message assistant chatbot-widget__typing">
            Assistant is typing...
          </div>
        </div>
        <div class="chatbot-widget__input">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage" 
            placeholder="Type your message..." 
          />
          <button @click="sendMessage" :disabled="!userInput.trim()">Send</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        isChatOpen: false,
        userInput: '',
        messages: [],
        socket: null,
        isTyping: false,
        isInitialized: false
      };
    },
    methods: {
      openChat() {
        this.isChatOpen = true;
        if (!this.isInitialized) {
          this.initializeWebSocket();
          this.messages.push({ from: 'assistant', text: 'Hello, how can I help you?' });
          this.isInitialized = true;
        }
        this.$nextTick(this.scrollToBottom);
      },
      closeChat() {
        this.isChatOpen = false;
        if (this.socket) {
          this.socket.close();
          this.socket = null;
        }
      },
      initializeWebSocket() {
        this.socket = new WebSocket('ws://localhost:8000');
  
        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          this.isTyping = false;
          this.messages.push({ from: 'assistant', text: data.message });
          this.$nextTick(this.scrollToBottom);
        };
  
        this.socket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
  
        this.socket.onclose = () => {
          console.log('WebSocket connection closed');
        };
      },
      sendMessage() {
        if (this.userInput.trim()) {
          this.messages.push({ from: 'user', text: this.userInput });
          if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ message: this.userInput }));
          } else {
            this.initializeWebSocket();
            this.socket.onopen = () => {
              this.socket.send(JSON.stringify({ message: this.userInput }));
            };
          }
          this.userInput = '';
          this.isTyping = true;
          this.$nextTick(this.scrollToBottom);
        }
      },
      scrollToBottom() {
        const container = this.$refs.messageContainer;
        container.scrollTop = container.scrollHeight;
      },
      formatMessage(text) {
        return text
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/^# (.*$)/gm, '<h1>$1</h1>')
          .replace(/^## (.*$)/gm, '<h2>$1</h2>')
          .replace(/^### (.*$)/gm, '<h3>$1</h3>')
          .replace(/\n/g, '<br>');
      }
    }
  };
  </script>


<style scoped>
.chatbot-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: Arial, sans-serif;
}

.chatbot-widget__toggle {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 15px 20px;
  font-size: 16px;
  border-radius: 25px;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.chatbot-widget__toggle:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.chatbot-widget__container {
  width: 300px;
  height: 400px;
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
}

.chatbot-widget__header {
  background-color: #4CAF50;
  color: white;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chatbot-widget__header h3 {
  margin: 0;
  font-size: 18px;
}

.chatbot-widget__close {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}

.chatbot-widget__messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 15px;
}

.chatbot-widget__message {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
}

.chatbot-widget__message.user {
  background-color: #e7f5fe;
  margin-left: auto;
  border-bottom-right-radius: 0;
}

.chatbot-widget__message.assistant {
  background-color: #f0f0f0;
  margin-right: auto;
  border-bottom-left-radius: 0;
}

.chatbot-widget__typing {
  font-style: italic;
  color: #888;
}

.chatbot-widget__input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #e0e0e0;
}

.chatbot-widget__input input {
  flex-grow: 1;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  padding: 8px 15px;
  font-size: 14px;
  outline: none;
}

.chatbot-widget__input button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 15px;
  margin-left: 10px;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.chatbot-widget__input button:hover:not(:disabled) {
  background-color: #45a049;
}

.chatbot-widget__input button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>