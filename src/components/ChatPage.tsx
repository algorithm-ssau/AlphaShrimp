import { useState, useEffect, useRef } from 'react'
import { Send } from 'lucide-react'
import { fetchModels, fetchChats, fetchMessages, sendMessage } from '../api'
import type { Model, ChatInfo, MessageInfo } from '../api'

const MODES = ['quality', 'balanced', 'economy'] as const

export default function ChatPage() {
    const [models, setModels] = useState<Model[]>([])
    const [chats, setChats] = useState<ChatInfo[]>([])
    const [messages, setMessages] = useState<MessageInfo[]>([])
    const [activeChatId, setActiveChatId] = useState<number | null>(null)

    const [input, setInput] = useState('')
    const [selectedModel, setSelectedModel] = useState<string>('auto')
    const [mode, setMode] = useState<typeof MODES[number]>('quality')
    const [loading, setLoading] = useState(false)

    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    useEffect(() => {
        fetchModels().then(setModels)
        fetchChats().then(setChats)
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const loadChat = async (chatId: number) => {
        setActiveChatId(chatId)
        const msgs = await fetchMessages(chatId)
        setMessages(msgs)
    }

    const startNewChat = () => {
        setActiveChatId(null)
        setMessages([])
        inputRef.current?.focus()
    }

    const handleSend = async () => {
        const text = input.trim()
        if (!text || loading) return

        setLoading(true)
        setInput('')

        const userMsg: MessageInfo = {
            id: Date.now(),
            role: 'user',
            content: text,
            model: null,
            category: null,
            created_at: new Date().toISOString(),
        }
        setMessages(prev => [...prev, userMsg])

        try {
            const result = await sendMessage(
                text,
                selectedModel === 'auto' ? null : selectedModel,
                mode,
                activeChatId
            )

            const assistantMsg: MessageInfo = {
                id: Date.now() + 1,
                role: 'assistant',
                content: result.reply,
                model: result.model,
                category: result.category,
                created_at: new Date().toISOString(),
            }
            setMessages(prev => [...prev, assistantMsg])

            if (!activeChatId) {
                setActiveChatId(result.chat_id)
            }

            // Refresh sidebar
            fetchChats().then(setChats)
        } catch {
            const errorMsg: MessageInfo = {
                id: Date.now() + 1,
                role: 'assistant',
                content: 'Ошибка соединения с сервером',
                model: null,
                category: null,
                created_at: new Date().toISOString(),
            }
            setMessages(prev => [...prev, errorMsg])
        }

        setLoading(false)
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="app-layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <img src="/alpha_shrimp_logo.jpeg" alt="Logo" className="sidebar-logo" />
                </div>

                <button className="new-chat-btn" onClick={startNewChat}>
                    + Новый чат
                </button>

                <div className="chat-list">
                    {chats.map(chat => (
                        <div
                            key={chat.id}
                            className={`chat-list-item ${chat.id === activeChatId ? 'active' : ''}`}
                            onClick={() => loadChat(chat.id)}
                        >
                            {chat.title}
                        </div>
                    ))}
                </div>
            </aside>

            {/* Main chat area */}
            <main className="chat-area">
                {/* Header with controls */}
                <header className="chat-header">
                    <div className="chat-header-left">
                        <select
                            className="model-selector"
                            value={selectedModel}
                            onChange={e => setSelectedModel(e.target.value)}
                        >
                            <option value="auto">🧠 Авто-роутинг</option>
                            {models.map(m => (
                                <option key={m.id} value={m.id}>
                                    {m.name}
                                </option>
                            ))}
                        </select>

                        {selectedModel === 'auto' && (
                            <div className="mode-switcher">
                                {MODES.map(m => (
                                    <button
                                        key={m}
                                        className={`mode-btn ${mode === m ? 'active' : ''}`}
                                        onClick={() => setMode(m)}
                                    >
                                        {m === 'quality' ? '⚡ Quality' :
                                            m === 'balanced' ? '⚖️ Balance' : '💰 Economy'}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                </header>

                {/* Messages */}
                {messages.length === 0 ? (
                    <div className="empty-state">
                        <img src="/alpha_shrimp_logo2.jpg" alt="" className="empty-state-icon" />
                        <h2>Начни диалог</h2>
                        <p>
                            Напиши что угодно — роутер определит категорию и выберет лучшую модель.
                            Или выбери модель вручную.
                        </p>
                    </div>
                ) : (
                    <div className="messages-container">
                        {messages.map(msg => (
                            <div key={msg.id} className={`message ${msg.role}`}>
                                <div className="message-bubble">{msg.content}</div>
                                <div className="message-meta">
                                    {msg.model && (
                                        <span className="message-model-tag">{msg.model}</span>
                                    )}
                                    {msg.category && (
                                        <span className="message-category-tag">{msg.category}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                )}

                {/* Input */}
                <div className="input-area">
                    <div className="input-wrapper">
                        <textarea
                            ref={inputRef}
                            className="input-field"
                            placeholder="Напишите сообщение..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            rows={1}
                            disabled={loading}
                        />
                        <button
                            className="send-btn"
                            onClick={handleSend}
                            disabled={!input.trim() || loading}
                        >
                            <Send />
                        </button>
                    </div>
                </div>
            </main>
        </div>
    )
}
