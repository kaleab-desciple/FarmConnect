import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const AIDiagnosticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [loading, setLoading] = useState(false);

  // Simulating the camera/photo feature
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const handleCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (event) => {
         setPreviewImage(event.target?.result as string);
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  const analyzePhoto = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setStep(2);
    }, 1500);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#f8f9fa] pb-24 pt-16">
      <div className="bg-white px-4 py-3 border-b border-gray-200 sticky top-16 z-30 shadow-sm flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="text-gray-500 font-bold active:scale-95">
          ← Back
        </button>
        <h1 className="text-lg font-bold text-gray-900 truncate px-4">Pocket Agronomist</h1>
        <div className="w-8"></div> {/* Spacer */}
      </div>

      <div className="p-4 flex-1 flex flex-col">
        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex flex-col h-full">
            <h2 className="font-bold text-gray-800 mb-1">Step 1: Snap & Analyze</h2>
            <p className="text-xs text-gray-500 mb-4">Take a clear photo of the affected crop leaf, fruit, or stem.</p>
            
            <div className="flex-1 bg-gray-100 border-2 border-dashed border-gray-300 rounded-xl mb-4 flex flex-col items-center justify-center overflow-hidden relative">
              {previewImage ? (
                <>
                  <img src={previewImage} alt="Crop scan preview" className="object-cover w-full h-full" />
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-4 flex justify-end">
                     <button onClick={() => fileInputRef.current?.click()} className="text-white text-xs font-bold underline bg-black/40 px-2 py-1 rounded backdrop-blur">
                       Retake
                     </button>
                  </div>
                </>
              ) : (
                <div className="text-center p-6">
                  <span className="text-5xl mb-2 block opacity-50">📸</span>
                  <p className="text-gray-500 font-bold mb-4">No photo selected</p>
                  <button onClick={() => fileInputRef.current?.click()} className="px-6 py-3 bg-white text-gray-800 border border-gray-300 rounded-lg shadow-sm font-bold active:scale-95 transition-all">
                    Open Camera
                  </button>
                </div>
              )}
              <input 
                type="file" 
                accept="image/*" 
                capture="environment"
                className="hidden" 
                ref={fileInputRef}
                onChange={handleCapture}
              />
            </div>

            <button 
              onClick={analyzePhoto}
              disabled={loading || !previewImage}
              className={`w-full py-4 rounded-xl font-bold text-white tracking-wider text-sm shadow-md transition-all ${
                (loading || !previewImage) ? 'bg-green-600/50 cursor-not-allowed' : 'bg-green-700 active:scale-[0.98]'
              }`}
            >
              {loading ? 'ANALYZING (via Edge ML)...' : 'ANALYZE PHOTO'}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-300">
             <div className="bg-red-50 p-4 border-b border-red-100 text-center">
               <span className="text-4xl mb-2 block">🚨</span>
               <h2 className="font-bold text-red-800 text-lg">Disease Detected</h2>
               <p className="text-sm text-red-600/80">High confidence match.</p>
             </div>
             
             <div className="p-5">
               <h3 className="font-bold text-gray-800 mb-3 uppercase text-xs">Differential Diagnosis</h3>
               <div className="space-y-3 mb-6">
                 <div className="p-3 border border-green-500 bg-green-50 rounded-lg flex items-center justify-between">
                   <div>
                     <h4 className="font-bold text-green-900">Late Blight</h4>
                     <p className="text-xs text-green-700">85% Match</p>
                   </div>
                   <button className="text-xs text-green-800 font-bold underline">Ref Photo</button>
                 </div>
                 <div className="p-3 border border-gray-200 rounded-lg flex items-center justify-between opacity-60">
                   <div>
                     <h4 className="font-bold text-gray-700">Spider Mite Damage</h4>
                     <p className="text-xs text-gray-500">10% Match</p>
                   </div>
                 </div>
               </div>

               <button onClick={() => setStep(3)} className="w-full py-3 bg-gray-900 text-white rounded-xl font-bold text-sm shadow-md active:scale-95">
                 View Treatment Options
               </button>
             </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h2 className="font-bold text-gray-800 mb-2">💡 Recommendation</h2>
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                Immediate application of Copper Fungicide is recommended to halt the spread. Ensure all infected leaves are removed and destroyed away from the field.
              </p>
              
              <div className="bg-green-50 text-green-800 p-3 rounded-lg border border-green-200 text-sm font-bold flex items-center justify-center cursor-pointer active:scale-95 shadow-sm">
                + Add Copper Fungicide to Next Tasks
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-10 text-6xl pointer-events-none">👨‍🌾</div>
               <h2 className="font-bold text-blue-900 mb-1 flex items-center gap-2">⚠️ Highly Recommended</h2>
               <p className="text-blue-700 text-xs mb-4 max-w-[80%]">Due to the severity of Late Blight, an expert opinion is advised.</p>
               
               <button className="w-full py-4 rounded-xl font-bold bg-blue-600 text-white tracking-wider text-sm shadow-md active:scale-[0.98] flex items-center justify-center gap-2 transition-all">
                 VERIFY WITH AGRONOMIST (FREE)
               </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIDiagnosticsPage;
