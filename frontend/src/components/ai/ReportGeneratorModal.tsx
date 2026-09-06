import React, { useState } from 'react';
import { aiService } from '../../services/aiService';
import { ReportResult } from '../../types/ai';
import { FileText, Download, CheckCircle2, Loader2, X } from 'lucide-react';
import { printOrDownloadPdf, SAMPLE_INTELLIGENCE_REPORTS } from '../../utils/reportPdfGenerator';

interface ReportGeneratorModalProps {
  aoiId: string;
  aoiName: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ReportGeneratorModal: React.FC<ReportGeneratorModalProps> = ({
  aoiId,
  aoiName,
  isOpen,
  onClose,
}) => {
  const [reportTitle, setReportTitle] = useState(
    `ORBIT Intelligence Brief: ${aoiName}`
  );
  const [format, setFormat] = useState<'PDF' | 'MARKDOWN' | 'JSON'>('PDF');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<ReportResult | null>(null);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsLoading(true);
    try {
      const apiFormat = format === 'PDF' ? 'MARKDOWN' : format;
      const res = await aiService.generateReport(aoiId, reportTitle, apiFormat);
      setGeneratedReport(res);
    } catch (err) {
      console.error('Failed to generate report', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!generatedReport) return;

    if (format === 'PDF') {
      const template = SAMPLE_INTELLIGENCE_REPORTS[0];
      const customReport = {
        ...template,
        title: reportTitle,
        aoi_name: aoiName,
        executive_summary: generatedReport.content_text.slice(0, 400) + '...',
        provenance_hash_sha256: generatedReport.provenance_hash_sha256,
      };
      printOrDownloadPdf(customReport);
      return;
    }

    const blob = new Blob([generatedReport.content_text], {
      type: format === 'MARKDOWN' ? 'text/markdown' : 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `orbit_report_${aoiId}_${Date.now()}.${format === 'MARKDOWN' ? 'md' : 'json'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-lg max-w-2xl w-full p-5 space-y-4 max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-100">
              CREATE CUSTOM SATELLITE REPORT
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        {!generatedReport ? (
          <div className="space-y-4 py-2">
            <div>
              <label className="block text-xs text-slate-300 font-medium mb-1">
                Report Title
              </label>
              <input
                type="text"
                value={reportTitle}
                onChange={(e) => setReportTitle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-300 font-medium mb-1">
                Choose Output Format
              </label>
              <div className="flex gap-3">
                {(['PDF', 'MARKDOWN', 'JSON'] as const).map((fmt) => (
                  <button
                    key={fmt}
                    type="button"
                    onClick={() => setFormat(fmt)}
                    className={`flex-1 py-2 rounded text-xs border transition-colors cursor-pointer ${
                      format === fmt
                        ? 'bg-cyan-950/80 border-cyan-500 text-cyan-200 font-bold'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-900'
                    }`}
                  >
                    {fmt === 'PDF' ? 'PDF (Printable Document)' : fmt}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-3 rounded bg-slate-950/80 border border-slate-800 text-xs text-slate-400 space-y-1.5 font-sans">
              <div className="text-[11px] text-cyan-400 font-bold uppercase tracking-wider">
                What this report will include:
              </div>
              <ul className="list-disc pl-4 space-y-1 text-[11px] text-slate-300">
                <li>Plain-language Executive Summary & area background</li>
                <li>Direct satellite measurements (before vs. after comparisons)</li>
                <li>Roads, human access, and construction activity correlation</li>
                <li>Independent radar verification to eliminate cloud interference</li>
                <li>5-year future outlook and trend predictions</li>
                <li>Digital tamper-proof seal (SHA-256) verifying authentic data</li>
              </ul>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="w-full py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 text-xs font-bold uppercase tracking-wider transition-colors flex items-center justify-center gap-2 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating Satellite Report...
                </>
              ) : (
                'Generate Report'
              )}
            </button>
          </div>
        ) : (
          <div className="space-y-4 flex-1 flex flex-col min-h-0">
            <div className="flex items-center justify-between p-2.5 rounded bg-emerald-950/40 border border-emerald-700/60 text-emerald-300 text-xs">
              <div className="flex items-center gap-2 font-mono">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Report Generated Successfully</span>
              </div>
              <span className="font-mono text-[10px] text-slate-400">
                Digest: {generatedReport.provenance_hash_sha256.slice(0, 16)}...
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-3 rounded bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap">
              {generatedReport.content_text}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleDownload}
                className="flex-1 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 cursor-pointer"
              >
                <Download className="w-4 h-4" />
                Download Report ({format})
              </button>
              <button
                onClick={() => setGeneratedReport(null)}
                className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs cursor-pointer"
              >
                Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
