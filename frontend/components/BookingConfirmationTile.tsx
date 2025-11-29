'use client'

interface BookingConfirmationTileProps {
  bookingReference: string
  bookingType: 'doctor' | 'lab'
  bookingDetail: string
  date: string
  amount: number
  onConfirm: () => void
  onCancel: () => void
}

export default function BookingConfirmationTile({
  bookingReference,
  bookingType,
  bookingDetail,
  date,
  amount,
  onConfirm,
  onCancel,
}: BookingConfirmationTileProps) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4 my-2">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-semibold text-slate-900">Booking Confirmation</h3>
        </div>
        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
          {bookingReference}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm">
          <span className="text-slate-600 w-24">Type:</span>
          <span className="font-medium text-slate-900">
            {bookingType === 'doctor' ? 'Doctor Appointment' : 'Lab Test'}
          </span>
        </div>
        <div className="flex items-center text-sm">
          <span className="text-slate-600 w-24">Detail:</span>
          <span className="font-medium text-slate-900">
            {bookingDetail && bookingDetail.trim()
              ? bookingDetail
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                  .join(' ')
              : bookingDetail}
          </span>
        </div>
        <div className="flex items-center text-sm">
          <span className="text-slate-600 w-24">Date & Time:</span>
          <span className="font-medium text-slate-900">{date}</span>
        </div>
        <div className="flex items-center text-sm">
          <span className="text-slate-600 w-24">Amount:</span>
          <span className="font-bold text-blue-600 text-lg">${amount.toFixed(2)}</span>
        </div>
      </div>

      <div className="flex space-x-2">
        <button
          onClick={onConfirm}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
        >
          Confirm & Proceed
        </button>
        <button
          onClick={onCancel}
          className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

