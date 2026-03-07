import { useState } from 'react';
import {
  WrenchScrewdriverIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { imageService } from '../../services/imageService';
import type { ImageGeneration } from '../../types';
import type {
  PromptEngineerDiagnoseResponse,
  PromptEngineerRepromptResponse,
  FailureCode,
} from '../../types/promptEngineering';
import { FAILURE_TAXONOMY, getFailureCodeColor } from '../../types/promptEngineering';

interface RepromptPanelProps {
  generatedImage: ImageGeneration;
  brandId: number;
  diagnosis?: PromptEngineerDiagnoseResponse;
  onRegenerate: (correctedPrompt: string) => void;
  onClose: () => void;
}

const MAX_ATTEMPTS = 3;

export function RepromptPanel({
  generatedImage,
  brandId,
  diagnosis,
  onRegenerate,
  onClose,
}: RepromptPanelProps) {
  const [attemptNumber, setAttemptNumber] = useState(1);
  const [failureDescription, setFailureDescription] = useState(
    diagnosis?.diagnosis || ''
  );
  const [isFixing, setIsFixing] = useState(false);
  const [repromptResult, setRepromptResult] = useState<PromptEngineerRepromptResponse | null>(null);
  const [error, setError] = useState('');
  const [showCorrectedPrompt, setShowCorrectedPrompt] = useState(false);

  const handleApplyFix = async () => {
    if (!failureDescription.trim()) return;
    setIsFixing(true);
    setError('');
    try {
      const result = await imageService.repromptImage({
        brand_id: brandId,
        original_prompt: generatedImage.prompt,
        failure_description: failureDescription,
        attempt_number: attemptNumber,
      });
      if (result.error) {
        setError(result.error);
      } else {
        setRepromptResult(result);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fix prompt';
      setError(message);
    } finally {
      setIsFixing(false);
    }
  };

  const handleRegenerate = () => {
    if (repromptResult?.corrected_prompt) {
      onRegenerate(repromptResult.corrected_prompt);
    }
  };

  const handleTryAgain = () => {
    if (attemptNumber < MAX_ATTEMPTS) {
      setAttemptNumber(attemptNumber + 1);
      setRepromptResult(null);
      setError('');
    }
  };

  const maxReached = attemptNumber >= MAX_ATTEMPTS && repromptResult !== null;

  return (
    <Card className="border-purple-500/20 bg-purple-500/5 mt-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <WrenchScrewdriverIcon className="w-5 h-5 text-purple-400" />
          <h4 className="font-semibold text-text-primary text-sm">Fix Image</h4>
        </div>
        <div className="flex items-center gap-3">
          {/* Attempt Counter */}
          <div className="flex items-center gap-1.5">
            {Array.from({ length: MAX_ATTEMPTS }).map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full ${
                  i < attemptNumber
                    ? 'bg-purple-400'
                    : 'bg-dark-500'
                }`}
              />
            ))}
            <span className="text-xs text-text-muted ml-1">
              {attemptNumber}/{MAX_ATTEMPTS}
            </span>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xs">
            Cancel
          </button>
        </div>
      </div>

      {/* Failure Codes from Diagnosis */}
      {diagnosis && diagnosis.failure_codes.length > 0 && !repromptResult && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {diagnosis.failure_codes.map((code) => {
            const info = FAILURE_TAXONOMY[code as FailureCode];
            const colorClass = getFailureCodeColor(code as FailureCode);
            return (
              <span
                key={code}
                className={`px-2 py-0.5 rounded border text-xs font-medium ${colorClass}`}
                title={info?.desc}
              >
                {code}
              </span>
            );
          })}
        </div>
      )}

      {/* Fix Input */}
      {!repromptResult && (
        <>
          <textarea
            value={failureDescription}
            onChange={(e) => setFailureDescription(e.target.value)}
            placeholder="Describe what needs to be fixed..."
            className="w-full px-3 py-2 bg-dark-600 border border-white/10 rounded-xl text-text-primary placeholder-text-muted text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 mb-3"
            rows={2}
          />

          {error && (
            <div className="p-2 bg-red-500/10 border border-red-500/20 rounded-lg mb-3">
              <p className="text-red-400 text-xs">{error}</p>
            </div>
          )}

          <Button
            fullWidth
            size="sm"
            variant="primary"
            onClick={handleApplyFix}
            isLoading={isFixing}
            disabled={!failureDescription.trim() || maxReached}
            leftIcon={<WrenchScrewdriverIcon className="w-4 h-4" />}
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            Apply Fix
          </Button>
        </>
      )}

      {/* Fix Results */}
      {repromptResult && (
        <div className="space-y-3">
          {/* Patches Applied */}
          {repromptResult.patches_applied && repromptResult.patches_applied.length > 0 && (
            <div>
              <p className="text-xs text-text-muted mb-2">Patches Applied</p>
              <div className="space-y-1.5">
                {repromptResult.patches_applied.map((patch, idx) => (
                  <div key={idx} className="flex items-start gap-2 p-2 bg-green-500/5 border border-green-500/10 rounded-lg">
                    <CheckCircleIcon className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-green-300 leading-relaxed">{patch}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Failure Codes from Reprompt */}
          {repromptResult.failure_codes && repromptResult.failure_codes.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {repromptResult.failure_codes.map((code) => {
                const info = FAILURE_TAXONOMY[code as FailureCode];
                const colorClass = getFailureCodeColor(code as FailureCode);
                return (
                  <span
                    key={code}
                    className={`px-2 py-0.5 rounded border text-xs font-medium ${colorClass}`}
                    title={info?.desc}
                  >
                    {code} {info?.name}
                  </span>
                );
              })}
            </div>
          )}

          {/* Corrected Prompt (collapsible) */}
          <div>
            <button
              onClick={() => setShowCorrectedPrompt(!showCorrectedPrompt)}
              className="text-xs text-purple-400 hover:text-purple-300 transition-colors"
            >
              {showCorrectedPrompt ? 'Hide' : 'Show'} corrected prompt
            </button>
            {showCorrectedPrompt && (
              <pre className="whitespace-pre-wrap text-xs text-text-secondary bg-dark-700/50 border border-white/5 rounded-xl p-3 mt-2 max-h-[150px] overflow-y-auto font-mono leading-relaxed">
                {repromptResult.corrected_prompt}
              </pre>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-1">
            {attemptNumber < MAX_ATTEMPTS && (
              <Button
                size="sm"
                variant="ghost"
                onClick={handleTryAgain}
                leftIcon={<ArrowPathIcon className="w-4 h-4" />}
                className="flex-1"
              >
                Try Another Fix
              </Button>
            )}
            <Button
              size="sm"
              variant="primary"
              onClick={handleRegenerate}
              className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              Regenerate Image
            </Button>
          </div>

          {/* Max attempts warning */}
          {maxReached && (
            <div className="flex items-center gap-2 p-2 bg-amber-500/10 border border-amber-500/20 rounded-lg">
              <ExclamationTriangleIcon className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <p className="text-xs text-amber-300">
                Maximum attempts reached. Try different settings or rewrite your prompt.
              </p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default RepromptPanel;
