import { useState, useEffect, useCallback } from 'react';
import { Modal } from '../ui';
import imageService from '../../services/imageService';
import type {
  CopySuggestion,
  OverlayPosition,
  FontStyle,
  TextAlignment,
  AIStyleVariant,
} from '../../types/copyOverlay';
import {
  SparklesIcon,
  PencilSquareIcon,
  CheckCircleIcon,
  ArrowPathIcon,
  SwatchIcon,
} from '@heroicons/react/24/outline';

interface CopyOverlayModalProps {
  isOpen: boolean;
  onClose: () => void;
  assetId: number;
  captionText: string;
  ctaText?: string;
  imageUrl: string;
  brandId?: number | null;
  onOverlayApplied: (newImageUrl: string) => void;
}

const POSITIONS: { value: OverlayPosition; label: string; icon: string }[] = [
  { value: 'top_banner', label: 'Top', icon: '▔' },
  { value: 'center', label: 'Center', icon: '⬤' },
  { value: 'bottom_banner', label: 'Bottom', icon: '▁' },
  { value: 'top_bottom_split', label: 'Split', icon: '⫿' },
];

const FONTS: { value: FontStyle; label: string; css: string }[] = [
  { value: 'montserrat_bold', label: 'Montserrat Bold', css: "'Montserrat', sans-serif" },
  { value: 'montserrat_regular', label: 'Montserrat', css: "'Montserrat', sans-serif" },
  { value: 'playfair_bold', label: 'Playfair Display', css: "'Playfair Display', serif" },
  { value: 'roboto_bold', label: 'Roboto Bold', css: "'Roboto', sans-serif" },
  { value: 'bebas_neue', label: 'Bebas Neue', css: "'Bebas Neue', sans-serif" },
];

const COLOR_PRESETS = [
  '#FFFFFF', '#000000', '#F59E0B', '#EF4444', '#3B82F6', '#10B981', '#8B5CF6', '#EC4899',
];

const STYLE_BADGES: Record<string, { bg: string; text: string }> = {
  bold: { bg: 'bg-red-500/20', text: 'text-red-400' },
  inspirational: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
  question: { bg: 'bg-yellow-500/20', text: 'text-yellow-400' },
  cta: { bg: 'bg-green-500/20', text: 'text-green-400' },
  minimal: { bg: 'bg-purple-500/20', text: 'text-purple-400' },
};

export function CopyOverlayModal({
  isOpen,
  onClose,
  assetId,
  captionText,
  ctaText,
  imageUrl,
  brandId,
  onOverlayApplied,
}: CopyOverlayModalProps) {
  // AI suggestions
  const [suggestions, setSuggestions] = useState<CopySuggestion[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  // Custom text mode
  const [useCustom, setUseCustom] = useState(false);
  const [customText, setCustomText] = useState('');

  // Manual styling
  const [position, setPosition] = useState<OverlayPosition>('bottom_banner');
  const [fontStyle, setFontStyle] = useState<FontStyle>('montserrat_bold');
  const [textColor, setTextColor] = useState('#FFFFFF');
  const [overlayOpacity, setOverlayOpacity] = useState(60);
  const [textAlignment, setTextAlignment] = useState<TextAlignment>('center');
  const [addTextShadow, setAddTextShadow] = useState(true);

  // AI Styles
  const [aiVariants, setAiVariants] = useState<AIStyleVariant[]>([]);
  const [loadingStyles, setLoadingStyles] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState<number | null>(null);
  const [showManualControls, setShowManualControls] = useState(false);

  // State
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState('');

  // The active copy text
  const activeText = useCustom ? customText : (selectedIdx !== null ? suggestions[selectedIdx]?.text : '');

  // Fetch suggestions on open
  const fetchSuggestions = useCallback(async () => {
    setLoadingSuggestions(true);
    setError('');
    try {
      const res = await imageService.generateCopySuggestions({
        brand_id: brandId || undefined,
        caption_text: captionText,
        cta_text: ctaText,
        count: 5,
      });
      setSuggestions(res.suggestions || []);
      if (res.suggestions?.length > 0) {
        setSelectedIdx(0);
        setPosition(res.suggestions[0].recommended_layout || 'bottom_banner');
      }
    } catch {
      setError('Failed to generate copy suggestions');
    } finally {
      setLoadingSuggestions(false);
    }
  }, [brandId, captionText, ctaText]);

  useEffect(() => {
    if (isOpen) {
      fetchSuggestions();
      // Reset state
      setAiVariants([]);
      setSelectedVariant(null);
      setShowManualControls(false);
    }
  }, [isOpen, fetchSuggestions]);

  // Generate AI style variants
  const handleGenerateAIStyles = async () => {
    if (!activeText.trim()) {
      setError('Select or write copy text first');
      return;
    }
    setLoadingStyles(true);
    setError('');
    setSelectedVariant(null);
    try {
      const res = await imageService.generateAIStyles(assetId, {
        copy_text: activeText.trim(),
        brand_id: brandId || undefined,
      });
      setAiVariants(res.variants || []);
      setShowManualControls(false);
    } catch {
      setError('Failed to generate AI styles');
    } finally {
      setLoadingStyles(false);
    }
  };

  // Apply selected AI variant
  const handleApplyVariant = async () => {
    if (selectedVariant === null || !aiVariants[selectedVariant]) return;
    const variant = aiVariants[selectedVariant];
    setApplying(true);
    setError('');
    try {
      const res = await imageService.applyCopyOverlay(assetId, {
        copy_text: activeText.trim(),
        position: variant.settings.position,
        font_style: variant.settings.font_style,
        text_color: variant.settings.text_color,
        overlay_opacity: variant.settings.overlay_opacity,
        font_size: 0,
        text_alignment: variant.settings.text_alignment,
        add_text_shadow: variant.settings.add_text_shadow,
      });
      if (res.overlay_image_url) {
        onOverlayApplied(res.overlay_image_url);
      }
    } catch {
      setError('Failed to apply overlay');
    } finally {
      setApplying(false);
    }
  };

  // Apply manual style
  const handleApplyManual = async () => {
    if (!activeText.trim()) {
      setError('Please select or write copy text');
      return;
    }
    setApplying(true);
    setError('');
    try {
      const res = await imageService.applyCopyOverlay(assetId, {
        copy_text: activeText.trim(),
        position,
        font_style: fontStyle,
        text_color: textColor,
        overlay_opacity: overlayOpacity,
        font_size: 0,
        text_alignment: textAlignment,
        add_text_shadow: addTextShadow,
      });
      if (res.overlay_image_url) {
        onOverlayApplied(res.overlay_image_url);
      }
    } catch {
      setError('Failed to apply overlay');
    } finally {
      setApplying(false);
    }
  };

  // CSS preview for manual mode
  const getPreviewStyle = (): React.CSSProperties => {
    const base: React.CSSProperties = {
      position: 'absolute',
      left: 0,
      right: 0,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      padding: '12px 16px',
      background: `rgba(0,0,0,${overlayOpacity / 100})`,
      textAlign: textAlignment as 'left' | 'center' | 'right',
      fontFamily: FONTS.find(f => f.value === fontStyle)?.css || 'sans-serif',
      fontWeight: fontStyle.includes('bold') || fontStyle === 'bebas_neue' ? 700 : 400,
      color: textColor,
      textShadow: addTextShadow ? '2px 2px 4px rgba(0,0,0,0.5)' : 'none',
      fontSize: 'clamp(12px, 3vw, 20px)',
      lineHeight: 1.3,
      letterSpacing: fontStyle === 'bebas_neue' ? '0.05em' : 'normal',
    };
    if (position === 'top_banner') return { ...base, top: '8%' };
    if (position === 'center') return { ...base, top: '50%', transform: 'translateY(-50%)' };
    return { ...base, bottom: '8%' };
  };

  // Whether we have AI variants to show
  const hasVariants = aiVariants.length > 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Copy Overlay" size="full">
      <div className="flex flex-col lg:flex-row gap-4 max-h-[75vh]">

        {/* Left — Preview Area */}
        <div className="lg:w-[58%] flex-shrink-0">
          {/* AI Style Variants Grid — shown when variants are generated */}
          {hasVariants && !showManualControls ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <p className="text-[10px] text-text-muted uppercase font-medium flex items-center gap-1">
                  <SwatchIcon className="w-3 h-3" /> AI-Designed Styles — Pick one
                </p>
                <button
                  onClick={handleGenerateAIStyles}
                  disabled={loadingStyles}
                  className="text-[10px] text-primary-400 hover:text-primary-300 flex items-center gap-1"
                >
                  <ArrowPathIcon className="w-3 h-3" /> Regenerate
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {aiVariants.map((v, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedVariant(i)}
                    className={`rounded-lg border overflow-hidden transition-all ${
                      selectedVariant === i
                        ? 'border-primary-500 ring-2 ring-primary-500/30 scale-[1.01]'
                        : 'border-white/10 hover:border-white/25'
                    }`}
                  >
                    <img
                      src={v.preview}
                      alt={v.name}
                      className="w-full object-contain max-h-[28vh]"
                    />
                    <div className="px-2 py-1.5 bg-dark-card/80 flex items-center justify-between">
                      <div>
                        <p className="text-[10px] font-medium text-text-primary">{v.name}</p>
                        <p className="text-[9px] text-text-muted">{v.description}</p>
                      </div>
                      {selectedVariant === i && (
                        <CheckCircleIcon className="w-4 h-4 text-primary-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Original image with CSS live preview — for manual mode or before AI styles */
            <div>
              <div className="relative rounded-lg overflow-hidden border border-white/10 bg-black/20">
                <img src={imageUrl} alt="Preview" className="w-full object-contain max-h-[60vh]" />
                {activeText && showManualControls && (
                  <div style={getPreviewStyle()}>
                    {activeText}
                  </div>
                )}
              </div>
              <p className="text-[10px] text-text-muted mt-1 text-center">
                {showManualControls ? 'Live preview — final render may differ slightly' : 'Select copy text, then generate AI styles'}
              </p>
            </div>
          )}
        </div>

        {/* Right — Controls */}
        <div className="lg:w-[42%] space-y-3 overflow-y-auto pr-1">

          {/* Step 1: Copy Text Selection */}
          <div>
            <p className="text-[10px] text-text-muted uppercase font-medium mb-1.5">Step 1: Choose Copy Text</p>

            {/* Tab Toggle */}
            <div className="flex gap-1 bg-dark-card rounded-lg p-0.5 mb-2">
              <button
                onClick={() => setUseCustom(false)}
                className={`flex-1 text-xs py-1.5 px-3 rounded-md transition-colors flex items-center justify-center gap-1 ${
                  !useCustom ? 'bg-primary-500/20 text-primary-400 font-medium' : 'text-text-muted hover:text-text-secondary'
                }`}
              >
                <SparklesIcon className="w-3 h-3" /> AI Suggestions
              </button>
              <button
                onClick={() => setUseCustom(true)}
                className={`flex-1 text-xs py-1.5 px-3 rounded-md transition-colors flex items-center justify-center gap-1 ${
                  useCustom ? 'bg-primary-500/20 text-primary-400 font-medium' : 'text-text-muted hover:text-text-secondary'
                }`}
              >
                <PencilSquareIcon className="w-3 h-3" /> Custom Text
              </button>
            </div>

            {/* AI Suggestions List */}
            {!useCustom && (
              <div className="space-y-1 max-h-[25vh] overflow-y-auto">
                {loadingSuggestions ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin h-4 w-4 border-b-2 border-primary-400 rounded-full" />
                    <span className="ml-2 text-xs text-text-muted">Generating copy ideas...</span>
                  </div>
                ) : suggestions.length > 0 ? (
                  <>
                    {suggestions.map((s, idx) => {
                      const badge = STYLE_BADGES[s.style] || STYLE_BADGES.bold;
                      return (
                        <button
                          key={idx}
                          onClick={() => {
                            setSelectedIdx(idx);
                            setPosition(s.recommended_layout || 'bottom_banner');
                            setSelectedVariant(null); // reset variant selection when text changes
                          }}
                          className={`w-full text-left p-2 rounded-lg border transition-all ${
                            selectedIdx === idx
                              ? 'border-primary-500/50 bg-primary-500/10'
                              : 'border-white/5 bg-dark-card hover:border-white/15'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <p className="text-xs text-text-primary font-medium leading-snug flex-1">{s.text}</p>
                            {selectedIdx === idx && <CheckCircleIcon className="w-3.5 h-3.5 text-primary-400 flex-shrink-0 mt-0.5" />}
                          </div>
                          <span className={`inline-block text-[8px] px-1.5 py-0.5 rounded mt-1 ${badge.bg} ${badge.text} uppercase font-medium`}>
                            {s.style}
                          </span>
                        </button>
                      );
                    })}
                    <button
                      onClick={fetchSuggestions}
                      disabled={loadingSuggestions}
                      className="text-[10px] text-primary-400 hover:text-primary-300 flex items-center gap-1 mx-auto"
                    >
                      <ArrowPathIcon className="w-3 h-3" /> Regenerate
                    </button>
                  </>
                ) : (
                  <p className="text-xs text-text-muted text-center py-3">No suggestions generated</p>
                )}
              </div>
            )}

            {/* Custom Text */}
            {useCustom && (
              <textarea
                value={customText}
                onChange={(e) => { setCustomText(e.target.value); setSelectedVariant(null); }}
                placeholder="Type your copy text here..."
                maxLength={200}
                rows={2}
                className="input w-full text-sm"
              />
            )}
          </div>

          {/* Step 2: Generate AI Styles */}
          <div className="border-t border-white/5 pt-2">
            <p className="text-[10px] text-text-muted uppercase font-medium mb-1.5">Step 2: Design Style</p>

            {/* AI Styles Button */}
            <button
              onClick={handleGenerateAIStyles}
              disabled={loadingStyles || !activeText.trim()}
              className="w-full text-xs py-2.5 px-4 rounded-lg border border-purple-500/30 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-colors flex items-center justify-center gap-2 disabled:opacity-40 font-medium"
            >
              {loadingStyles ? (
                <>
                  <div className="animate-spin h-3.5 w-3.5 border-b-2 border-purple-400 rounded-full" />
                  AI is designing 4 styles...
                </>
              ) : (
                <>
                  <SwatchIcon className="w-4 h-4" />
                  Generate AI Styles
                </>
              )}
            </button>

            {/* Toggle manual controls */}
            <button
              onClick={() => { setShowManualControls(!showManualControls); setSelectedVariant(null); }}
              className="text-[10px] text-text-muted hover:text-text-secondary mt-1.5 mx-auto flex items-center gap-1"
            >
              {showManualControls ? 'Hide' : 'Or'} customize manually
            </button>
          </div>

          {/* Manual Styling Controls (collapsible) */}
          {showManualControls && (
            <div className="border border-white/5 rounded-lg p-2.5 space-y-2 bg-dark-card/50">
              {/* Position */}
              <div>
                <label className="text-[10px] text-text-muted mb-1 block">Position</label>
                <div className="flex gap-1">
                  {POSITIONS.map((p) => (
                    <button
                      key={p.value}
                      onClick={() => setPosition(p.value)}
                      className={`flex-1 text-xs py-1.5 rounded-md border transition-colors ${
                        position === p.value
                          ? 'border-primary-500/50 bg-primary-500/15 text-primary-400'
                          : 'border-white/10 text-text-muted hover:border-white/20'
                      }`}
                    >
                      <span className="block text-base leading-none">{p.icon}</span>
                      <span className="text-[9px]">{p.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Font */}
              <div>
                <label className="text-[10px] text-text-muted mb-1 block">Font</label>
                <select
                  value={fontStyle}
                  onChange={(e) => setFontStyle(e.target.value as FontStyle)}
                  className="input w-full text-xs py-1.5"
                >
                  {FONTS.map((f) => (
                    <option key={f.value} value={f.value}>{f.label}</option>
                  ))}
                </select>
              </div>

              {/* Text Color */}
              <div>
                <label className="text-[10px] text-text-muted mb-1 block">Text Color</label>
                <div className="flex items-center gap-1.5 flex-wrap">
                  {COLOR_PRESETS.map((c) => (
                    <button
                      key={c}
                      onClick={() => setTextColor(c)}
                      className={`w-5 h-5 rounded-full border-2 transition-transform ${
                        textColor === c ? 'border-primary-400 scale-110' : 'border-white/20'
                      }`}
                      style={{ backgroundColor: c }}
                    />
                  ))}
                  <input
                    type="text"
                    value={textColor}
                    onChange={(e) => setTextColor(e.target.value)}
                    maxLength={7}
                    className="input w-16 text-[10px] py-1 px-2"
                    placeholder="#FFFFFF"
                  />
                </div>
              </div>

              {/* Opacity + Alignment + Shadow */}
              <div>
                <label className="text-[10px] text-text-muted mb-1 flex justify-between">
                  <span>Background Opacity</span>
                  <span className="text-text-secondary">{overlayOpacity}%</span>
                </label>
                <input
                  type="range"
                  min={0} max={100}
                  value={overlayOpacity}
                  onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                  className="w-full accent-primary-500 h-1"
                />
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <label className="text-[10px] text-text-muted mb-1 block">Align</label>
                  <div className="flex gap-1">
                    {(['left', 'center', 'right'] as TextAlignment[]).map((a) => (
                      <button
                        key={a}
                        onClick={() => setTextAlignment(a)}
                        className={`flex-1 text-[10px] py-1 rounded border transition-colors ${
                          textAlignment === a
                            ? 'border-primary-500/50 bg-primary-500/15 text-primary-400'
                            : 'border-white/10 text-text-muted'
                        }`}
                      >
                        {a === 'left' ? '◧' : a === 'center' ? '⬤' : '◨'}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-[10px] text-text-muted mb-1 block">Shadow</label>
                  <button
                    onClick={() => setAddTextShadow(!addTextShadow)}
                    className={`text-[10px] py-1 px-3 rounded border transition-colors ${
                      addTextShadow
                        ? 'border-primary-500/50 bg-primary-500/15 text-primary-400'
                        : 'border-white/10 text-text-muted'
                    }`}
                  >
                    {addTextShadow ? 'ON' : 'OFF'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              <p className="text-xs text-red-400">{error}</p>
            </div>
          )}

          {/* Apply Button — different based on mode */}
          {selectedVariant !== null && hasVariants && !showManualControls ? (
            <button
              onClick={handleApplyVariant}
              disabled={applying}
              className="w-full btn-primary text-sm py-2.5 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-400 hover:to-pink-400 disabled:opacity-50"
            >
              {applying ? (
                <>
                  <div className="animate-spin h-4 w-4 border-b-2 border-white rounded-full" />
                  Applying {aiVariants[selectedVariant]?.name}...
                </>
              ) : (
                <>
                  <CheckCircleIcon className="w-4 h-4" />
                  Apply "{aiVariants[selectedVariant]?.name}"
                </>
              )}
            </button>
          ) : showManualControls ? (
            <button
              onClick={handleApplyManual}
              disabled={applying || !activeText.trim()}
              className="w-full btn-primary text-sm py-2.5 flex items-center justify-center gap-2 bg-gradient-to-r from-primary-500 to-pink-500 hover:from-primary-400 hover:to-pink-400 disabled:opacity-50"
            >
              {applying ? (
                <>
                  <div className="animate-spin h-4 w-4 border-b-2 border-white rounded-full" />
                  Applying Overlay...
                </>
              ) : (
                <>
                  <SparklesIcon className="w-4 h-4" />
                  Apply Custom Style
                </>
              )}
            </button>
          ) : null}
        </div>
      </div>
    </Modal>
  );
}

export default CopyOverlayModal;
