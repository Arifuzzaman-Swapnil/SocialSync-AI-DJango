import { useState } from 'react';
import {
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { imageService } from '../../services/imageService';
import type { ImageGeneration } from '../../types';
import type {
  PromptEngineerDiagnoseResponse,
  FailureCode,
} from '../../types/promptEngineering';
import { FAILURE_TAXONOMY, getFailureCodeColor } from '../../types/promptEngineering';

interface ImageDiagnosisModalProps {
  isOpen: boolean;
  onClose: () => void;
  generatedImage: ImageGeneration;
  onStartReprompt: (diagnosis: PromptEngineerDiagnoseResponse) => void;
}

const severityColors: Record<string, string> = {
  minor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
  moderate: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  major: 'text-red-400 bg-red-500/10 border-red-500/20',
};

export function ImageDiagnosisModal({
  isOpen,
  onClose,
  generatedImage,
  onStartReprompt,
}: ImageDiagnosisModalProps) {
  const [description, setDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [diagnosis, setDiagnosis] = useState<PromptEngineerDiagnoseResponse | null>(null);
  const [error, setError] = useState('');

  const handleDiagnose = async () => {
    if (!description.trim()) return;
    setIsAnalyzing(true);
    setError('');
    try {
      const result = await imageService.diagnoseImage({
        image_description: description,
        original_prompt: generatedImage.prompt,
        revised_prompt: generatedImage.revised_prompt || '',
      });
      if (result.error) {
        setError(result.error);
      } else {
        setDiagnosis(result);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to diagnose image';
      setError(message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFixIt = () => {
    if (diagnosis) {
      onStartReprompt(diagnosis);
      handleClose();
    }
  };

  const handleClose = () => {
    setDescription('');
    setDiagnosis(null);
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Diagnose Image Issues" size="xl">
      <div className="space-y-4">
        {/* Context: Image + Prompt */}
        <div className="flex gap-4">
          {generatedImage.generated_image && (
            <div className="w-24 h-24 flex-shrink-0 rounded-xl overflow-hidden bg-dark-700">
              <img
                src={generatedImage.generated_image}
                alt="Generated"
                className="w-full h-full object-cover"
              />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-xs text-text-muted mb-1">Original prompt</p>
            <p className="text-sm text-text-secondary line-clamp-3">{generatedImage.prompt}</p>
          </div>
        </div>

        {/* Diagnosis Input */}
        {!diagnosis && (
          <>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                What's wrong with this image?
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., The colors are too dark, there's unwanted text, the background is cluttered..."
                className="w-full px-4 py-3 bg-dark-600 border border-white/10 rounded-xl text-text-primary placeholder-text-muted text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/30"
                rows={3}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <Button
              fullWidth
              size="md"
              variant="primary"
              onClick={handleDiagnose}
              isLoading={isAnalyzing}
              disabled={!description.trim()}
              leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              Diagnose
            </Button>
          </>
        )}

        {/* Diagnosis Results */}
        {diagnosis && (
          <div className="space-y-4">
            {/* Failure Codes */}
            <div>
              <p className="text-xs text-text-muted mb-2">Identified Issues</p>
              <div className="flex flex-wrap gap-2">
                {diagnosis.failure_codes.map((code) => {
                  const info = FAILURE_TAXONOMY[code as FailureCode];
                  const colorClass = getFailureCodeColor(code as FailureCode);
                  return (
                    <div
                      key={code}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-medium ${colorClass}`}
                      title={info?.desc || code}
                    >
                      <span className="font-bold">{code}</span>
                      {info && <span className="ml-1.5 opacity-80">{info.name}</span>}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Severity */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-text-muted">Severity:</span>
              <span
                className={`px-2.5 py-1 rounded-lg border text-xs font-medium capitalize ${
                  severityColors[diagnosis.severity] || severityColors.moderate
                }`}
              >
                {diagnosis.severity}
              </span>
              {diagnosis.is_systemic && (
                <span className="px-2.5 py-1 rounded-lg border text-xs font-medium text-orange-400 bg-orange-500/10 border-orange-500/20">
                  Systemic
                </span>
              )}
            </div>

            {/* Diagnosis Text */}
            <div className="p-3 bg-dark-700/50 rounded-xl">
              <p className="text-sm text-text-secondary">{diagnosis.diagnosis}</p>
            </div>

            {/* Recommendation */}
            <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl">
              <p className="text-xs text-purple-400 font-medium mb-1">Recommendation</p>
              <p className="text-sm text-purple-300">{diagnosis.recommendation}</p>
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Button size="sm" variant="ghost" onClick={handleClose} className="flex-1">
                Close
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={handleFixIt}
                leftIcon={<ExclamationTriangleIcon className="w-4 h-4" />}
                className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                Fix with Re-prompt
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

export default ImageDiagnosisModal;
