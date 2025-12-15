'use client'

interface BookingConfirmationTileProps {
  bookingReference: string
  bookingType: 'doctor' | 'lab'
  bookingDetail: string
  date: string
  amount: number
  status?: 'booked' | 'cancelled' | 'rescheduled' | 'pending'
  onConfirm: () => void
  onCancel: () => void
}

export default function BookingConfirmationTile({
  bookingReference,
  bookingType,
  bookingDetail,
  date,
  amount,
  status = 'pending',
  onConfirm,
  onCancel,
}: BookingConfirmationTileProps) {
  // Determine title, icon, and colors based on status
  const getStatusConfig = () => {
    switch (status) {
      case 'cancelled':
        return {
          title: 'Appointment Cancelled',
          icon: (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ),
          bgColor: 'bg-red-500',
          borderColor: 'border-red-200',
          bgGradient: 'from-red-50 to-orange-50',
          badgeColor: 'bg-red-100 text-red-700',
        }
      case 'rescheduled':
        return {
          title: 'Appointment Rescheduled',
          icon: (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          ),
          bgColor: 'bg-yellow-500',
          borderColor: 'border-yellow-200',
          bgGradient: 'from-yellow-50 to-amber-50',
          badgeColor: 'bg-yellow-100 text-yellow-700',
        }
      case 'booked':
        return {
          title: 'Appointment Confirmed',
          icon: (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          bgColor: 'bg-green-500',
          borderColor: 'border-green-200',
          bgGradient: 'from-green-50 to-emerald-50',
          badgeColor: 'bg-green-100 text-green-700',
        }
      default: // pending
        return {
          title: 'Booking Confirmation',
          icon: (
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ),
          bgColor: 'bg-blue-500',
          borderColor: 'border-blue-200',
          bgGradient: 'from-blue-50 to-indigo-50',
          badgeColor: 'bg-blue-100 text-blue-700',
        }
    }
  }

  const statusConfig = getStatusConfig()
  const showButtons = status === 'pending'

  return (
    <div className={`bg-gradient-to-br ${statusConfig.bgGradient} border-2 ${statusConfig.borderColor} rounded-xl p-4 my-2`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 ${statusConfig.bgColor} rounded-full flex items-center justify-center`}>
            {statusConfig.icon}
          </div>
          <h3 className="font-semibold text-slate-900">{statusConfig.title}</h3>
        </div>
        <span className={`text-xs ${statusConfig.badgeColor} px-2 py-1 rounded-full font-medium`}>
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
        {status !== 'cancelled' && amount > 0 && (
          <div className="flex items-center text-sm">
            <span className="text-slate-600 w-24">Amount:</span>
            <span className={`font-bold text-lg ${status === 'booked' ? 'text-green-600' : status === 'rescheduled' ? 'text-yellow-600' : 'text-blue-600'}`}>
              ${amount.toFixed(2)}
            </span>
          </div>
        )}
      </div>

      {showButtons && (
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
      )}
    </div>
  )
}

