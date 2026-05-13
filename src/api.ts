const API_BASE = '/api'

export interface Model {
    id: string
    name: string
    provider: string
}

export interface ChatInfo {
    id: number
    title: string
    updated_at: string
}

export interface MessageInfo {
    id: number
    role: 'user' | 'assistant'
    content: string
    model: string | null
    category: string | null
    created_at: string
}

export interface ChatResponse {
    chat_id: number
    model: string
    category: string | null
    reply: string
}

export async function fetchModels(): Promise<Model[]> {
    const res = await fetch(`${API_BASE}/models`)
    return res.json()
}

export async function fetchChats(): Promise<ChatInfo[]> {
    const res = await fetch(`${API_BASE}/chats`)
    return res.json()
}

export async function fetchMessages(chatId: number): Promise<MessageInfo[]> {
    const res = await fetch(`${API_BASE}/chats/${chatId}/messages`)
    return res.json()
}

export async function sendMessage(
    message: string,
    model: string | null,
    mode: string,
    chatId: number | null
): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            message,
            model,
            mode,
            chat_id: chatId,
        }),
    })
    return res.json()
}
