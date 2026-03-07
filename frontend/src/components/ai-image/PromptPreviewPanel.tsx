import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  SparklesIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Spinner } from '../ui/Spinner';
import { imageService } from '../../services/imageService';
import type { PromptEngineerGenerateResponse } from '../../types/promptEngineering';

interface PromptPreviewPanelProps {
  brandId: number;
  subject: string;
  platform?: string;
  mood?: string;
  onUsePrompt: (prompt: string) => void;
  onGenerateWithPrompt: (prompt: string) => void;
  onClose: () => void;
}

export function PromptPreviewPanel({
  brandId,
  subject,
  platform = 'instagram',
  mood,
  onUsePrompt,
  onGenerateWithPrompt,
  onClose,
}: PromptPreviewPanelProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PromptEngineerGenerateResponse | null>(null);
  const [selectedVariation, setSelectedVariation] = useState(-1); // -1 = primary
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [showVariations, setShowVariations] = useState(false);

  const fetchEngineeredPrompt = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await imageService.generateEngineeredPrompt({
        brand_id: brandId,
        subject,
        platform,
        mood: mood || '',
      });
      if (data.error) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to generate engineered prompt';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedPrompt =
    result
      ? selectedVariation === -1
        ? result.primary_prompt
        : result.variations[selectedVariation]
      : '';

  const handleCopy = async () => {
    if (!selectedPrompt) return;
    await navigator.clipboard.writeText(selectedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Auto-fetch on mount
  if (!result && !isLoading && !error) {
    fetchEngineeredPrompt();
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-purple-500/20 bg-purple-500/5">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <SparklesIcon className="w-5 h-5 text-purple-400" />
            <h4 className="font-semibold text-text-primary text-sm">Engineered Prompt Preview</h4>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-dark-600 transition-colors">
            <XMarkIcon className="w-4 h-4 text-text-muted" />
          </button>
        </div>

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-8">
            <Spinner size="md" />
            <p className="mt-3 text-text-secondary text-sm">Engineering 9-layer prompt...</p>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl mb-3">
            <p className="text-red-400 text-sm">{error}</p>
            <Button size="sm" variant="ghost" onClick={fetchEngineeredPrompt} className="mt-2">
              Retry
            </Button>
          </div>
        )}

        {result && (
          <div className="space-y-3">
            {/* Brand Style Anchor */}
            {result.brand_style_anchor && (
              <div className="px-3 py-2 bg-purple-500/10 rounded-lg">
                <p className="text-purple-300 text-xs font-medium">{result.brand_style_anchor}</p>
              </div>
            )}

            {/* Primary Prompt */}
            <div className="relative">
              <div
                className={`rounded-xl border ${
                  selectedVariation === -1
                    ? 'border-purple-500/40 bg-purple-500/5'
                    : 'border-white/5 bg-dark-700/50'
                } cursor-pointer transition-colors`}
                onClick={() => setSelectedVariation(-1)}
              >
                <div className="flex items-center justify-between px-3 py-2 border-b border-white/5">
                  <span className="text-xs font-medium text-purple-400">Primary Prompt</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopy();
                    }}
                    className="p-1 rounded hover:bg-dark-600 transition-colors"
                  >
                    {copied ? (
                      <CheckIcon className="w-3.5 h-3.5 text-green-400" />
                    ) : (
                      <ClipboardDocumentIcon className="w-3.5 h-3.5 text-text-muted" />
                    )}
                  </button>
                </div>
                <pre className="whitespace-pre-wrap text-sm text-text-secondary p-3 max-h-[200px] overflow-y-auto font-mono leading-relaxed">
                  {result.primary_prompt}
                </pre>
              </div>
            </div>

            {/* Variations Toggle */}
            {result.variations && result.variations.length > 0 && (
              <div>
                <button
                  onClick={() => setShowVariations(!showVariations)}
                  className="flex items-center gap-1 text-xs text-text-muted hover:text-text-secondary transition-colors"
                >
                  {showVariations ? (
                    <ChevronUpIcon className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDownIcon className="w-3.5 h-3.5" />
                  )}
                  {result.variations.length} variation{result.variations.length > 1 ? 's' : ''} available
                </button>

                <AnimatePresence>
                  {showVariations && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="space-y-2 mt-2"
                    >
                      {result.variations.map((variation, idx) => (
                        <div
                          key={idx}
                          className={`rounded-xl border p-3 cursor-pointer transition-colors ${
                            selectedVariation === idx
                              ? 'border-purple-500/40 bg-purple-500/5'
                              : 'border-white/5 bg-dark-700/50 hover:border-white/10'
                          }`}
                          onClick={() => setSelectedVariation(idx)}
                        >
                          <span className="text-xs font-medium text-text-muted mb-1 block">
                            Variation {idx + 1}
                          </span>
                          <p className="text-sm text-text-secondary line-clamp-3">{variation}</p>
                        </div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}

            {/* Platform Notes */}
            {result.platform_notes && (
              <p className="text-xs text-text-muted italic px-1">{result.platform_notes}</p>
            )}

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onUsePrompt(selectedPrompt)}
                className="flex-1"
              >
                Use This Prompt
              </Button>
              <Button
                size="sm"
                variant="primary"
                onClick={() => onGenerateWithPrompt(selectedPrompt)}
                leftIcon={<SparklesIcon className="w-4 h-4" />}
                className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                Generate with This
              </Button>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  );
}

export default PromptPreviewPanel;
