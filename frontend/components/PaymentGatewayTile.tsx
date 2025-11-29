'use client'

import { useState } from 'react'

interface PaymentGatewayTileProps {
  bookingReference: string
  amount: number
  onPay: (paymentData: string) => void
  onCancel: () => void
}

export default function PaymentGatewayTile({
  bookingReference,
  amount,
  onPay,
  onCancel,
}: PaymentGatewayTileProps) {
  const [cardNumber, setCardNumber] = useState('')
  const [expiry, setExpiry] = useState('')
  const [cvv, setCvv] = useState('')
  const [cardholderName, setCardholderName] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // For POC, any data is accepted
    const paymentData = JSON.stringify({
      cardNumber: cardNumber || 'mock_card',
      expiry: expiry || '12/25',
      cvv: cvv || '123',
      cardholderName: cardholderName || 'Mock User',
    })
    onPay(paymentData)
  }

  return (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-4 my-2">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
          </div>
          <h3 className="font-semibold text-slate-900">Payment Gateway</h3>
        </div>
        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
          Secure Payment
        </span>
      </div>

      <div className="mb-3">
        <div className="text-sm text-slate-600 mb-1">Booking Reference:</div>
        <div className="font-mono text-sm font-semibold text-slate-900">{bookingReference}</div>
        <div className="text-lg font-bold text-green-600 mt-2">Total Amount: ${amount.toFixed(2)}</div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">Cardholder Name</label>
          <input
            type="text"
            value={cardholderName}
            onChange={(e) => setCardholderName(e.target.value)}
            placeholder="John Doe"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">Card Number</label>
          <input
            type="text"
            value={cardNumber}
            onChange={(e) => setCardNumber(e.target.value.replace(/\D/g, '').slice(0, 16))}
            placeholder="1234 5678 9012 3456"
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none font-mono"
            maxLength={16}
          />
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Expiry (MM/YY)</label>
            <input
              type="text"
              value={expiry}
              onChange={(e) => {
                let val = e.target.value.replace(/\D/g, '')
                if (val.length >= 2) val = val.slice(0, 2) + '/' + val.slice(2, 4)
                setExpiry(val.slice(0, 5))
              }}
              placeholder="12/25"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
              maxLength={5}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">CVV</label>
            <input
              type="text"
              value={cvv}
              onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').slice(0, 3))}
              placeholder="123"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
              maxLength={3}
            />
          </div>
        </div>

        <div className="flex space-x-2 pt-2">
          <button
            type="submit"
            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            Pay ${amount.toFixed(2)}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
        </div>

        <p className="text-xs text-slate-500 text-center mt-2">
          🔒 For POC: Any payment data will be accepted as successful
        </p>
      </form>
    </div>
  )
}

