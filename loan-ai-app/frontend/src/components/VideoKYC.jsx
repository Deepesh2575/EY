import { useState, useRef, useEffect, useCallback } from 'react'
import { Camera, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react'

export default function VideoKYC({ onCapture, onCancel }) {
    const videoRef = useRef(null)
    const [stream, setStream] = useState(null)
    const [error, setError] = useState(null)
    const [isCaptured, setIsCaptured] = useState(false)
    const [capturedImage, setCapturedImage] = useState(null)

    const stopCamera = useCallback(() => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop())
            setStream(null)
        }
    }, [stream])

    const startCamera = useCallback(async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' },
                audio: false
            })
            setStream(mediaStream)
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream
            }
            setError(null)
        } catch (err) {
            console.error("Camera error:", err)
            setError("Unable to access camera. Please allow permission.")
        }
    }, [])

    useEffect(() => {
        startCamera()
        return () => stopCamera()
    }, [startCamera, stopCamera])

    const handleCapture = () => {
        if (videoRef.current) {
            const canvas = document.createElement('canvas')
            canvas.width = videoRef.current.videoWidth
            canvas.height = videoRef.current.videoHeight
            const ctx = canvas.getContext('2d')
            ctx.drawImage(videoRef.current, 0, 0)

            canvas.toBlob((blob) => {
                const file = new File([blob], "kyc_selfie.jpg", { type: "image/jpeg" })
                setCapturedImage(URL.createObjectURL(blob))
                setIsCaptured(true)
                // Pass file back to parent immediately or after user confirmation?
                // Let's ask for confirmation.
                onCapture(file)
            }, 'image/jpeg', 0.8)
        }
    }

    const handleRetake = () => {
        setIsCaptured(false)
        setCapturedImage(null)
        onCapture(null) // Clear parent
    }

    if (error) {
        return (
            <div className="p-6 bg-dark-800 rounded-xl border border-danger-500/30 text-center">
                <AlertCircle className="w-12 h-12 text-danger-400 mx-auto mb-2" />
                <p className="text-danger-300 mb-4">{error}</p>
                <button
                    onClick={startCamera}
                    className="px-4 py-2 bg-dark-700 hover:bg-dark-600 rounded-lg text-white transition-colors"
                >
                    Try Again
                </button>
            </div>
        )
    }

    return (
        <div className="w-full max-w-md mx-auto bg-dark-800 rounded-xl border border-dark-600 overflow-hidden shadow-2xl animate-fade-in">
            <div className="p-4 border-b border-dark-700 flex justify-between items-center">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Camera className="w-5 h-5 text-primary-400" />
                    Video KYC Verification
                </h3>
                {onCancel && (
                    <button onClick={onCancel} className="text-dark-400 hover:text-white">
                        &times;
                    </button>
                )}
            </div>

            <div className="relative aspect-video bg-black">
                {!isCaptured ? (
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        className="w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                    />
                ) : (
                    <img
                        src={capturedImage}
                        alt="Captured"
                        className="w-full h-full object-cover transform scale-x-[-1]"
                    />
                )}

                {/* Overlay Instructions */}
                {!isCaptured && (
                    <div className="absolute bottom-4 left-0 right-0 text-center pointer-events-none">
                        <span className="px-3 py-1 bg-black/50 text-white text-sm rounded-full backdrop-blur-sm">
                            Position your face in the center
                        </span>
                    </div>
                )}
            </div>

            <div className="p-4 flex justify-center gap-4 bg-dark-800">
                {!isCaptured ? (
                    <button
                        onClick={handleCapture}
                        className="flex items-center gap-2 px-6 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-full font-medium transition-all transform hover:scale-105"
                    >
                        <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                        Capture Photo
                    </button>
                ) : (
                    <>
                        <button
                            onClick={handleRetake}
                            className="flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 text-dark-200 rounded-lg transition-colors"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Retake
                        </button>
                        <div className="flex items-center gap-2 text-success-400 font-medium animate-fade-in">
                            <CheckCircle className="w-5 h-5" />
                            <span>Uploading...</span>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}
