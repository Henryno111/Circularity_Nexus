'use client';

import { useState, useRef } from 'react';
import { 
  Upload, 
  Camera, 
  Trash2, 
  CheckCircle, 
  Loader2,
  Leaf,
  Coins,
  X
} from 'lucide-react';

interface WasteSubmission {
  id: string;
  image: string;
  wasteType: string;
  quantity: number;
  quality: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'UNUSABLE';
  estimatedValue: number;
  carbonImpact: number;
  status: 'pending' | 'validating' | 'approved' | 'rejected';
  timestamp: string;
}

interface AIAnalysis {
  wasteType: string;
  confidence: number;
  quantity: number;
  quality: 'EXCELLENT' | 'GOOD' | 'FAIR' | 'POOR' | 'UNUSABLE';
  estimatedValue: number;
  carbonImpact: number;
  recyclingTips: string[];
}

export default function SubmitWaste() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [submissions, setSubmissions] = useState<WasteSubmission[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setAnalysis(null);
    }
  };

  const handleCameraCapture = () => {
    fileInputRef.current?.click();
  };

  const analyzeWaste = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    
    try {
      // TODO: Replace with actual API call to your backend
      // const formData = new FormData();
      // formData.append('image', selectedFile);
      // const response = await fetch('/api/v1/ai/analyze', {
      //   method: 'POST',
      //   body: formData
      // });
      // const data = await response.json();
      
      // Mock AI analysis for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockAnalysis: AIAnalysis = {
        wasteType: 'PET Plastic',
        confidence: 0.95,
        quantity: 1.2,
        quality: 'EXCELLENT',
        estimatedValue: 0.15,
        carbonImpact: 1.8,
        recyclingTips: [
          'Rinse thoroughly before recycling',
          'Remove caps and labels if possible',
          'Flatten to save space in recycling bins'
        ]
      };
      
      setAnalysis(mockAnalysis);
    } catch (error) {
      console.error('Error analyzing waste:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const submitWaste = async () => {
    if (!analysis) return;

    setIsSubmitting(true);
    
    try {
      // TODO: Replace with actual API call to your backend
      // const response = await fetch('/api/v1/waste/submit', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     wasteType: analysis.wasteType,
      //     quantity: analysis.quantity,
      //     quality: analysis.quality,
      //     image: previewUrl
      //   })
      // });
      // const data = await response.json();
      
      // Mock submission
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const newSubmission: WasteSubmission = {
        id: Date.now().toString(),
        image: previewUrl,
        wasteType: analysis.wasteType,
        quantity: analysis.quantity,
        quality: analysis.quality,
        estimatedValue: analysis.estimatedValue,
        carbonImpact: analysis.carbonImpact,
        status: 'approved',
        timestamp: new Date().toISOString()
      };
      
      setSubmissions(prev => [newSubmission, ...prev]);
      setSelectedFile(null);
      setPreviewUrl('');
      setAnalysis(null);
    } catch (error) {
      console.error('Error submitting waste:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    setAnalysis(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-emerald-950">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 xl:px-16 2xl:px-24 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Submit Waste for Tokenization
          </h1>
          <p className="text-gray-600 dark:text-emerald-200">
            Upload a photo of your waste to get AI analysis and mint tokens
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            {/* File Upload */}
            <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Upload Waste Photo
              </h3>
              
              {!previewUrl ? (
                <div className="border-2 border-dashed border-gray-300 dark:border-emerald-700 rounded-xl p-8 text-center hover:border-emerald-500 dark:hover:border-emerald-500 transition-colors">
                  <Upload className="w-12 h-12 text-gray-400 dark:text-emerald-600 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-emerald-300 mb-4">
                    Drag and drop your waste photo here, or click to browse
                  </p>
                  <div className="flex gap-4 justify-center">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Browse Files
                    </button>
                    <button
                      onClick={handleCameraCapture}
                      className="flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                      <Camera className="w-4 h-4 mr-2" />
                      Take Photo
                    </button>
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <img
                    src={previewUrl}
                    alt="Waste preview"
                    className="w-full h-64 object-cover rounded-xl"
                  />
                  <button
                    onClick={removeFile}
                    className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              
              {selectedFile && !analysis && (
                <button
                  onClick={analyzeWaste}
                  disabled={isAnalyzing}
                  className="w-full mt-4 flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 disabled:opacity-50 text-white rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Leaf className="w-5 h-5 mr-2" />
                      Analyze with AI
                    </>
                  )}
                </button>
              )}
            </div>

            {/* AI Analysis Results */}
            {analysis && (
              <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  AI Analysis Results
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Waste Type</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{analysis.wasteType}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Confidence</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{(analysis.confidence * 100).toFixed(1)}%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Quantity</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{analysis.quantity} kg</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Quality</span>
                    <span className={`font-semibold px-3 py-1 rounded-full text-sm ${
                      analysis.quality === 'EXCELLENT' ? 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-300' :
                      analysis.quality === 'GOOD' ? 'bg-blue-100 text-blue-800 dark:bg-blue-800/50 dark:text-blue-300' :
                      analysis.quality === 'FAIR' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-300' :
                      analysis.quality === 'POOR' ? 'bg-orange-100 text-orange-800 dark:bg-orange-800/50 dark:text-orange-300' :
                      'bg-red-100 text-red-800 dark:bg-red-800/50 dark:text-red-300'
                    }`}>
                      {analysis.quality}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Estimated Value</span>
                    <span className="font-semibold text-gray-900 dark:text-white">${analysis.estimatedValue.toFixed(2)}</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-800/50 rounded-xl">
                    <span className="text-gray-700 dark:text-emerald-300">Carbon Impact</span>
                    <span className="font-semibold text-gray-900 dark:text-white">{analysis.carbonImpact} kg CO2 saved</span>
                  </div>
                </div>
                
                <button
                  onClick={submitWaste}
                  disabled={isSubmitting}
                  className="w-full mt-6 flex items-center justify-center px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 disabled:opacity-50 text-white rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Minting Tokens...
                    </>
                  ) : (
                    <>
                      <Coins className="w-5 h-5 mr-2" />
                      Mint Tokens
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Recent Submissions */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Recent Submissions
              </h3>
              
              {submissions.length === 0 ? (
                <div className="text-center py-8">
                  <Trash2 className="w-12 h-12 text-gray-400 dark:text-emerald-600 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-emerald-300">
                    No submissions yet. Upload your first waste photo to get started!
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {submissions.map((submission) => (
                    <div key={submission.id} className="flex items-center p-4 bg-gray-50 dark:bg-emerald-800/50 rounded-xl">
                      <img
                        src={submission.image}
                        alt={submission.wasteType}
                        className="w-16 h-16 object-cover rounded-lg mr-4"
                      />
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900 dark:text-white">
                          {submission.wasteType}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-emerald-300">
                          {submission.quantity} kg • {submission.quality}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-emerald-300">
                          {new Date(submission.timestamp).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-gray-900 dark:text-white">
                          ${submission.estimatedValue.toFixed(2)}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-emerald-300">
                          {submission.carbonImpact} kg CO2
                        </div>
                        <div className={`text-sm px-2 py-1 rounded-full ${
                          submission.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-800/50 dark:text-green-300' :
                          submission.status === 'pending' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/50 dark:text-yellow-300' :
                          'bg-red-100 text-red-800 dark:bg-red-800/50 dark:text-red-300'
                        }`}>
                          {submission.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recycling Tips */}
            {analysis && (
              <div className="bg-white dark:bg-emerald-900 rounded-2xl p-6 shadow-lg border border-gray-200 dark:border-emerald-800">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Recycling Tips
                </h3>
                
                <div className="space-y-3">
                  {analysis.recyclingTips.map((tip, index) => (
                    <div key={index} className="flex items-start p-3 bg-emerald-50 dark:bg-emerald-800/50 rounded-lg">
                      <CheckCircle className="w-5 h-5 text-emerald-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700 dark:text-emerald-300">{tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 