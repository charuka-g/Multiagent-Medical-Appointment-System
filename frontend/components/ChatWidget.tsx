'use client'

import { useState, useRef, useEffect } from 'react'
import BookingConfirmationTile from './BookingConfirmationTile'
import PaymentGatewayTile from './PaymentGatewayTile'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
  bookingData?: {
    type: 'confirmation' | 'payment'
    bookingReference?: string
    bookingType?: 'doctor' | 'lab'
    bookingDetail?: string
    date?: string
    amount?: number
  }
}

interface ChatWidgetProps {
  idNumber: number
}

export default function ChatWidget({ idNumber }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    if (isOpen) {
      scrollToBottom()
      inputRef.current?.focus()
    }
  }, [messages, isOpen])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/backend/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_number: idNumber,
          messages: userMessage.content,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from server')
      }

      const data = await response.json()
      
      // Extract the last AI message from the response
      // Backend returns {"messages": [...]}
      let assistantMessage = ''
      let messagesArray: any[] = []
      
      if (data.messages && Array.isArray(data.messages)) {
        messagesArray = data.messages
      } else if (Array.isArray(data)) {
        messagesArray = data
      } else {
        assistantMessage = 'Unexpected response format from server'
      }
      
      if (messagesArray.length > 0) {
        // Find the last AI message in the array
        const lastAIMessage = messagesArray
          .slice()
          .reverse()
          .find((msg: any) => {
            // Check various possible formats
            return msg.type === 'ai' || 
                   msg.role === 'assistant' || 
                   msg.constructor?.name === 'AIMessage' ||
                   (typeof msg === 'object' && msg.content && !msg.type) // Fallback for AI messages
          })
        
        if (lastAIMessage) {
          assistantMessage = lastAIMessage.content || lastAIMessage.text || JSON.stringify(lastAIMessage)
        } else {
          // Fallback: get the last message that's not from the user
          let lastUserMsgIndex = -1
          for (let i = messagesArray.length - 1; i >= 0; i--) {
            const msg = messagesArray[i]
            if (msg.type === 'human' || msg.role === 'user') {
              lastUserMsgIndex = i
              break
            }
          }
          if (lastUserMsgIndex >= 0 && lastUserMsgIndex < messagesArray.length - 1) {
            const lastMsg = messagesArray[messagesArray.length - 1]
            assistantMessage = lastMsg?.content || lastMsg?.text || JSON.stringify(lastMsg)
          } else {
            assistantMessage = 'No response from assistant'
          }
        }
      }

      // Parse message for booking confirmation or payment requests
      const bookingData = parseBookingMessage(assistantMessage)

      const aiMessage: Message = {
        role: 'assistant',
        content: assistantMessage,
        timestamp: new Date(),
        bookingData: bookingData,
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running on http://localhost:8000',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const parseBookingMessage = (message: string): Message['bookingData'] | undefined => {
    // Parse BOOKING_CREATED message
    const bookingCreatedMatch = message.match(/BOOKING_CREATED: Booking reference (\w+).*?(?:Doctor|Test): ([^,]+).*?Date: ([^,]+).*?Amount: \$([\d.]+)/i)
    if (bookingCreatedMatch) {
      const [, ref, detail, date, amount] = bookingCreatedMatch
      const isDoctor = message.toLowerCase().includes('doctor')
      return {
        type: 'confirmation',
        bookingReference: ref,
        bookingType: isDoctor ? 'doctor' : 'lab',
        bookingDetail: detail.trim(),
        date: date.trim(),
        amount: parseFloat(amount),
      }
    }

    // Parse BOOKING_CONFIRMED message (should show payment)
    const bookingConfirmedMatch = message.match(/BOOKING_CONFIRMED: Booking (\w+).*?Amount: \$([\d.]+)/i)
    if (bookingConfirmedMatch && message.toLowerCase().includes('proceeding to payment')) {
      const [, ref, amount] = bookingConfirmedMatch
      // Extract booking details from previous context or message
      const detailMatch = message.match(/(?:Doctor Appointment|Lab Test): ([^,]+)/i)
      const dateMatch = message.match(/Date: ([^,]+)/i)
      const isDoctor = message.toLowerCase().includes('doctor appointment')
      
      return {
        type: 'payment',
        bookingReference: ref,
        bookingType: isDoctor ? 'doctor' : 'lab',
        bookingDetail: detailMatch ? detailMatch[1].trim() : '',
        date: dateMatch ? dateMatch[1].trim() : '',
        amount: parseFloat(amount),
      }
    }

    return undefined
  }

  const handleConfirmBooking = async (bookingReference: string) => {
    // Send confirmation message to backend
    const confirmMessage: Message = {
      role: 'user',
      content: `confirm booking ${bookingReference}`,
      timestamp: new Date(),
    }
    
    setMessages((prev) => [...prev, confirmMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/backend/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_number: idNumber,
          messages: confirmMessage.content,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from server')
      }

      const data = await response.json()
      let assistantMessage = ''
      let messagesArray: any[] = []
      
      if (data.messages && Array.isArray(data.messages)) {
        messagesArray = data.messages
      } else if (Array.isArray(data)) {
        messagesArray = data
      }
      
      if (messagesArray.length > 0) {
        const lastAIMessage = messagesArray
          .slice()
          .reverse()
          .find((msg: any) => {
            return msg.type === 'ai' || 
                   msg.role === 'assistant' || 
                   msg.constructor?.name === 'AIMessage' ||
                   (typeof msg === 'object' && msg.content && !msg.type)
          })
        
        if (lastAIMessage) {
          assistantMessage = lastAIMessage.content || lastAIMessage.text || JSON.stringify(lastAIMessage)
        }
      }

      const bookingData = parseBookingMessage(assistantMessage)
      const aiMessage: Message = {
        role: 'assistant',
        content: assistantMessage,
        timestamp: new Date(),
        bookingData: bookingData,
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error('Error confirming booking:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePayment = async (bookingReference: string, paymentData: string) => {
    // Send payment message to backend
    const paymentMessage: Message = {
      role: 'user',
      content: `process payment for ${bookingReference} with payment data: ${paymentData}`,
      timestamp: new Date(),
    }
    
    setMessages((prev) => [...prev, paymentMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/backend/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_number: idNumber,
          messages: paymentMessage.content,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from server')
      }

      const data = await response.json()
      let assistantMessage = ''
      let messagesArray: any[] = []
      
      if (data.messages && Array.isArray(data.messages)) {
        messagesArray = data.messages
      } else if (Array.isArray(data)) {
        messagesArray = data
      }
      
      if (messagesArray.length > 0) {
        const lastAIMessage = messagesArray
          .slice()
          .reverse()
          .find((msg: any) => {
            return msg.type === 'ai' || 
                   msg.role === 'assistant' || 
                   msg.constructor?.name === 'AIMessage' ||
                   (typeof msg === 'object' && msg.content && !msg.type)
          })
        
        if (lastAIMessage) {
          assistantMessage = lastAIMessage.content || lastAIMessage.text || JSON.stringify(lastAIMessage)
        }
      }

      const aiMessage: Message = {
        role: 'assistant',
        content: assistantMessage,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error('Error processing payment:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 md:bottom-6 md:right-6 w-14 h-14 md:w-16 md:h-16 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-2xl hover:shadow-3xl flex items-center justify-center transition-all duration-300 transform hover:scale-110 active:scale-95 z-50 group"
          aria-label="Open chat"
        >
          <svg
            className="w-7 h-7 transition-transform group-hover:scale-110"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
          {/* Notification badge */}
          {messages.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold">
              {messages.length}
            </span>
          )}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 md:bottom-6 md:right-6 w-[calc(100vw-2rem)] md:w-[500px] lg:w-[600px] h-[calc(100vh-2rem)] md:h-[700px] lg:h-[800px] max-h-[800px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-slate-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-sm">Medical Assistant</h3>
                <p className="text-xs text-primary-100">We're here to help</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 bg-slate-50 space-y-3">
            {messages.length === 0 && (
              <div className="text-center py-8">
                <div className="inline-block p-3 bg-primary-100 rounded-full mb-3">
                  <svg
                    className="w-6 h-6 text-primary-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">
                  Hi! How can I help you today?
                </h4>
                <p className="text-xs text-slate-600">
                  Ask me about scheduling appointments
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className="max-w-[80%]">
                  {/* Show booking tiles if present */}
                  {message.bookingData?.type === 'confirmation' && message.bookingData.bookingReference && (
                    <BookingConfirmationTile
                      bookingReference={message.bookingData.bookingReference}
                      bookingType={message.bookingData.bookingType || 'doctor'}
                      bookingDetail={message.bookingData.bookingDetail || ''}
                      date={message.bookingData.date || ''}
                      amount={message.bookingData.amount || 0}
                      onConfirm={() => handleConfirmBooking(message.bookingData!.bookingReference!)}
                      onCancel={() => {}}
                    />
                  )}
                  
                  {message.bookingData?.type === 'payment' && message.bookingData.bookingReference && (
                    <PaymentGatewayTile
                      bookingReference={message.bookingData.bookingReference}
                      amount={message.bookingData.amount || 0}
                      onPay={(paymentData) => handlePayment(message.bookingData!.bookingReference!, paymentData)}
                      onCancel={() => {}}
                    />
                  )}

                  {/* Regular message content */}
                  <div
                    className={`rounded-lg px-3 py-2 text-sm ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-slate-900 shadow-sm border border-slate-200'
                    }`}
                  >
                    <div className="whitespace-pre-wrap break-words">{message.content}</div>
                    {message.timestamp && (
                      <div
                        className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-primary-100' : 'text-slate-500'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-slate-900 shadow-sm border border-slate-200 rounded-lg px-3 py-2">
                  <div className="flex space-x-1.5">
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="bg-white border-t border-slate-200 p-3">
            <div className="flex items-end space-x-2">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  rows={1}
                  className="w-full px-3 py-2 pr-10 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none transition-all max-h-24"
                  style={{
                    minHeight: '40px',
                    height: 'auto',
                  }}
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement
                    target.style.height = 'auto'
                    target.style.height = `${Math.min(target.scrollHeight, 96)}px`
                  }}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white p-2.5 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 flex-shrink-0"
                aria-label="Send message"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2 text-center">
              Patient ID: {idNumber}
            </p>
          </div>
        </div>
      )}
    </>
  )
}

