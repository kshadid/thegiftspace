import React, { useState } from 'react';
import { DEFAULT_REGISTRY_IMAGES, DEFAULT_FUND_IMAGES, getImagesByCategory } from '../utils/defaultImages';

export default function ImageSelector({ 
  selectedImage, 
  onImageSelect, 
  category = 'general',
  type = 'fund' // 'fund' or 'registry'
}) {
  const [showSelector, setShowSelector] = useState(false);
  
  const images = type === 'registry' 
    ? DEFAULT_REGISTRY_IMAGES 
    : getImagesByCategory(category);

  return (
    <div className="space-y-4">
      {/* Current Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Cover Image</label>
        <div className="relative">
          {selectedImage ? (
            <div className="relative w-full h-32 rounded-lg overflow-hidden bg-gray-100">
              <img 
                src={selectedImage} 
                alt="Selected cover" 
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                <button
                  onClick={() => setShowSelector(true)}
                  className="bg-white text-gray-900 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors"
                >
                  Change Image
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowSelector(true)}
              className="w-full h-32 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center text-gray-600 hover:border-gray-400 transition-colors"
            >
              <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm">Choose Beautiful Image</span>
            </button>
          )}
        </div>
      </div>

      {/* Image Selection Modal */}
      {showSelector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">
                  Choose {type === 'registry' ? 'Registry' : 'Fund'} Image
                </h3>
                <button
                  onClick={() => setShowSelector(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {images.map((image) => (
                  <div key={image.id} className="space-y-2">
                    <div 
                      className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:ring-2 hover:ring-rose-500 transition-all"
                      onClick={() => {
                        onImageSelect(image.url);
                        setShowSelector(false);
                      }}
                    >
                      <img 
                        src={image.url} 
                        alt={image.title}
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                        <div className="bg-white text-gray-900 px-3 py-1 rounded text-sm font-medium">
                          Select
                        </div>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-medium text-gray-900">{image.title}</p>
                      <p className="text-xs text-gray-600">{image.description}</p>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 text-center">
                  All images are professionally curated and royalty-free. You can also upload your own custom images.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}