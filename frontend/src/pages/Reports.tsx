import React, { useState } from 'react';
import {
  Download,
  FileText,
  Eye,
  CheckCircle2,
  X,
  Printer,
  ShieldCheck,
} from 'lucide-react';
import {
  SAMPLE_INTELLIGENCE_REPORTS,
  IntelligenceReportItem,
  printOrDownloadPdf,
  downloadReportMarkdown,
} from '../utils/reportPdfGenerator';
import { ReportGeneratorModal } from '../components/ai/ReportGeneratorModal';

export const Reports: React.FC = () => {
  const [reports] = useState<IntelligenceReportItem[]>(SAMPLE_INTELLIGENCE_REPORTS);
  const [selectedReport, setSelectedReport] = useState<IntelligenceReportItem | null>(null);
  const [isCompileModalOpen, setIsCompileModalOpen] = useState<boolean>(false);
  const [downloadSuccessMsg, setDownloadSuccessMsg] = useState<string | null>(null);

  const handleDownloadPdf = (report: IntelligenceReportItem) => {
    printOrDownloadPdf(report);
    setDownloadSuccessMsg(`Generated defense-grade printable PDF for "${report.title}"`);
    setTimeout(() => setDownloadSuccessMsg(null), 4000);
  };

  const handleDownloadMarkdown = (report: IntelligenceReportItem) => {
    downloadReportMarkdown(report);
    setDownloadSuccessMsg(`Downloaded structured Markdown dossier for "${report.title}"`);
    setTimeout(() => setDownloadSuccessMsg(null), 4000);
  };

  return (
    <div className="p-6 space-y-6 overflow-y-auto h-full font-sans" data-testid="reports-page">
      {/* Toast Notification */}
      {downloadSuccessMsg && (
        <div className="fixed top-4 right-4 z-50 bg-emerald-950 border border-orbit-emerald text-emerald-200 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-2 font-mono text-xs animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="w-4 h-4 text-orbit-emerald shrink-0" />
          <span>{downloadSuccessMsg}</span>
        </div>
      )}

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-orbit-border/60 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold tracking-widest text-orbit-emerald bg-emerald-950/60 px-2.5 py-1 rounded border border-orbit-emerald/40 uppercase">
              SATELLITE INTELLIGENCE BRIEFS
            </span>
          </div>
          <h1 className="text-xl font-bold text-orbit-text mt-1">
            Environmental & Intelligence Reports
          </h1>
          <p className="text-xs text-orbit-muted font-sans mt-0.5">
            Verified satellite reports analyzing deforestation, water loss, and urban growth with 100% authentic measurements.
          </p>
        </div>

        <button
          onClick={() => setIsCompileModalOpen(true)}
          className="px-4 py-2 bg-orbit-emerald text-orbit-void font-bold text-xs rounded-lg flex items-center gap-1.5 shadow-glow-emerald transition hover:bg-emerald-400 shrink-0 cursor-pointer"
        >
          <Printer className="w-4 h-4" />
          <span>Create Custom Report</span>
        </button>
      </div>

      {/* Reports Grid / Cards */}
      <div className="space-y-4">
        {reports.map((rep) => (
          <div
            key={rep.id}
            className="bg-orbit-carbon border border-orbit-border rounded-xl p-5 space-y-4 text-xs shadow-sm hover:border-orbit-emerald/40 transition"
          >
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
              <div className="space-y-1.5 max-w-3xl">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[10px] font-bold text-orbit-emerald bg-emerald-950/60 px-2.5 py-0.5 rounded border border-orbit-emerald/30">
                    {rep.status}
                  </span>
                  <span className="text-[10px] text-orbit-muted uppercase tracking-wider">{rep.type}</span>
                  <span className="text-[10px] text-orbit-muted/70 font-mono">• {rep.id}</span>
                </div>
                <h2 className="text-base font-bold text-orbit-text font-sans">{rep.title}</h2>
                <p className="text-xs text-orbit-muted font-sans leading-relaxed">{rep.executive_summary}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap md:flex-col lg:flex-row items-center gap-2 shrink-0">
                <button
                  onClick={() => setSelectedReport(rep)}
                  className="px-3 py-2 bg-orbit-slate/80 hover:bg-orbit-slate text-orbit-text font-medium rounded-lg border border-orbit-border flex items-center gap-1.5 transition text-xs cursor-pointer"
                  title="Read Full Report On Screen"
                >
                  <Eye className="w-3.5 h-3.5 text-orbit-sky" />
                  <span>Read Report</span>
                </button>

                <button
                  onClick={() => handleDownloadPdf(rep)}
                  className="px-3.5 py-2 bg-orbit-emerald hover:bg-emerald-400 text-orbit-void font-bold rounded-lg flex items-center gap-1.5 transition text-xs shadow-sm cursor-pointer"
                  title="Generate and Download High-Res PDF"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </button>

                <button
                  onClick={() => handleDownloadMarkdown(rep)}
                  className="px-3 py-2 bg-orbit-slate/40 hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text font-medium rounded-lg border border-orbit-border/60 flex items-center gap-1.5 transition text-xs cursor-pointer"
                  title="Download Markdown Document"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Markdown (.md)</span>
                </button>
              </div>
            </div>

            {/* Telemetry Snapshot Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-orbit-border/50 text-[11px]">
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40">
                <div className="text-[10px] text-orbit-muted uppercase font-medium">Measured Change</div>
                <div className="font-bold text-orbit-critical mt-0.5">{rep.telemetry.detected_change_area}</div>
              </div>
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40">
                <div className="text-[10px] text-orbit-muted uppercase font-medium">Vegetation / Greenness</div>
                <div className="font-bold text-amber-400 mt-0.5">{rep.telemetry.mean_ndvi_drop.split(' ')[0]} {rep.telemetry.mean_ndvi_drop.split(' ')[1] || ''}</div>
              </div>
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40">
                <div className="text-[10px] text-orbit-muted uppercase font-medium">Nearby Access</div>
                <div className="font-bold text-orbit-text mt-0.5">{rep.infrastructure_correlation.proximity_buffer}</div>
              </div>
              <div className="bg-orbit-slate/30 p-2.5 rounded-lg border border-orbit-border/40">
                <div className="text-[10px] text-orbit-muted uppercase font-medium">Satellite Evidence</div>
                <div className="font-bold text-orbit-emerald mt-0.5">{rep.sensor_corroboration.evidence_strength.split('(')[0]}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Interactive On-Screen Report Reader */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 font-sans">
          <div className="bg-orbit-carbon border border-orbit-border rounded-xl max-w-4xl w-full p-6 space-y-5 max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3 border-b border-orbit-border">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded bg-emerald-950 border border-orbit-emerald/60 text-orbit-emerald">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-orbit-text">
                    {selectedReport.title}
                  </h3>
                  <p className="text-[11px] text-orbit-muted">
                    {selectedReport.id} • {selectedReport.aoi_name} • Coordinates: {selectedReport.coordinates}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownloadPdf(selectedReport)}
                  className="px-3 py-1.5 bg-orbit-emerald hover:bg-emerald-400 text-orbit-void font-bold text-xs rounded-lg flex items-center gap-1.5 transition cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </button>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="p-1.5 rounded-lg hover:bg-orbit-slate text-orbit-muted hover:text-orbit-text transition cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Scrollable Body */}
            <div className="space-y-6 overflow-y-auto pr-2 text-xs text-orbit-text leading-relaxed">
              {/* Executive Summary */}
              <div className="p-4 bg-orbit-slate/30 border-l-4 border-orbit-emerald rounded-r-lg space-y-1.5">
                <div className="font-bold text-xs text-orbit-emerald uppercase tracking-wider">
                  Executive Summary
                </div>
                <p className="text-orbit-text leading-relaxed text-[13px]">{selectedReport.executive_summary}</p>
              </div>

              {/* Section 1: Measured Satellite Telemetry */}
              <div className="space-y-2">
                <div className="font-bold text-orbit-emerald uppercase text-xs tracking-wider">
                  1. Satellite Measurements & Facts
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[12px]">
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Earlier Photo Date:</span>{' '}
                    <span className="text-orbit-text font-bold">{selectedReport.telemetry.baseline_date}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Recent Photo Date:</span>{' '}
                    <span className="text-orbit-text font-bold">{selectedReport.telemetry.target_date}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Optical Satellite:</span>{' '}
                    <span className="text-orbit-text">{selectedReport.telemetry.sensor_optical}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Radar Satellite:</span>{' '}
                    <span className="text-orbit-text">{selectedReport.telemetry.sensor_radar}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Total Area Monitored:</span>{' '}
                    <span className="text-orbit-text">{selectedReport.telemetry.total_area_analyzed}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                    <span className="text-orbit-muted font-medium">Measured Change Area:</span>{' '}
                    <span className="text-orbit-critical font-bold">{selectedReport.telemetry.detected_change_area}</span>
                  </div>
                  <div className="p-3 bg-orbit-slate/20 rounded-lg border border-orbit-border/50 sm:col-span-2">
                    <span className="text-orbit-muted font-medium">Greenness / Surface Shift:</span>{' '}
                    <span className="text-amber-400 font-bold">{selectedReport.telemetry.mean_ndvi_drop}</span>
                  </div>
                </div>
              </div>

              {/* Section 2: Infrastructure & Forecasting */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="space-y-2 p-3.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                  <div className="font-bold text-orbit-sky uppercase text-xs">
                    2. Roads & Nearby Human Activity
                  </div>
                  <div className="space-y-1.5 text-[12px]">
                    <div><span className="text-orbit-muted">Main Highway Nearby:</span> <span className="font-medium text-orbit-text">{selectedReport.infrastructure_correlation.primary_highway}</span></div>
                    <div><span className="text-orbit-muted">Distance from Road:</span> <span className="font-medium text-orbit-text">{selectedReport.infrastructure_correlation.proximity_buffer}</span></div>
                    <div><span className="text-orbit-muted">New Dirt Roads:</span> <span className="font-medium text-orbit-text">{selectedReport.infrastructure_correlation.new_spurs_detected} new access tracks</span></div>
                    <div><span className="text-orbit-muted">Priority Level:</span> <span className="text-orbit-critical font-bold">{selectedReport.infrastructure_correlation.access_threat_level}</span></div>
                  </div>
                </div>

                <div className="space-y-2 p-3.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/50">
                  <div className="font-bold text-orbit-emerald uppercase text-xs">
                    3. 5-Year Future Forecast (Based on Past Trends)
                  </div>
                  <div className="space-y-1.5 text-[12px]">
                    <div><span className="text-orbit-muted">Forecast Period:</span> <span className="font-medium text-orbit-text">{selectedReport.forecasting_projection.horizon}</span></div>
                    <div><span className="text-orbit-muted">Estimated Impact:</span> <span className="font-medium text-orbit-text">{selectedReport.forecasting_projection.projected_loss_hectares}</span></div>
                    <div><span className="text-orbit-muted">Expected Range:</span> <span className="font-medium text-orbit-text">{selectedReport.forecasting_projection.confidence_interval_95}</span></div>
                    <div><span className="text-orbit-muted">Historical Accuracy:</span> <span className="text-orbit-emerald font-bold">{selectedReport.forecasting_projection.backtest_accuracy}</span></div>
                  </div>
                </div>
              </div>

              {/* Section 3: Key Findings */}
              <div className="space-y-2">
                <div className="font-bold text-orbit-emerald uppercase text-xs tracking-wider">
                  4. Key Environmental Findings
                </div>
                <div className="space-y-1.5">
                  {selectedReport.key_findings.map((finding, idx) => (
                    <div key={idx} className="p-2.5 bg-orbit-slate/20 rounded-lg border border-orbit-border/40 text-[12px] flex items-start gap-2">
                      <span className="w-5 h-5 rounded-full bg-emerald-950 text-orbit-emerald font-bold flex items-center justify-center shrink-0 text-[10px]">
                        {idx + 1}
                      </span>
                      <span className="text-orbit-text">{finding}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 4: Grounded Evidence Claims */}
              <div className="space-y-2">
                <div className="font-bold text-orbit-emerald uppercase text-xs tracking-wider">
                  5. Verified Facts & Satellite Evidence
                </div>
                <div className="space-y-2">
                  {selectedReport.grounded_claims.map((c) => (
                    <div key={c.id} className="p-3 bg-orbit-slate/30 border border-orbit-border rounded-lg text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-orbit-emerald">[{c.id}]</span>
                        <span className="text-[11px] font-bold text-orbit-emerald bg-emerald-950/60 px-2 py-0.5 rounded border border-orbit-emerald/30">
                          {c.confidence}
                        </span>
                      </div>
                      <div className="text-orbit-text text-[12px]">{c.claim_text}</div>
                      <div className="text-[11px] text-orbit-muted">Evidence Source: <span className="text-orbit-sky font-medium">{c.evidence_id}</span></div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Section 5: Cryptographic Provenance */}
              <div className="p-3 bg-orbit-slate/40 border border-orbit-border/80 rounded-lg text-[11px] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <div className="text-orbit-muted uppercase text-[10px] font-bold">🔒 Digital Tamper-Proof Seal (SHA-256)</div>
                  <div className="text-orbit-emerald font-mono text-[10px] break-all mt-0.5">{selectedReport.provenance_hash_sha256}</div>
                  <div className="text-orbit-muted text-[10px] mt-0.5">Guarantees these satellite calculations are authentic and have not been altered.</div>
                </div>
                <span className="text-[10px] font-bold bg-emerald-950 px-2.5 py-1.5 rounded text-orbit-emerald border border-orbit-emerald/40 shrink-0">
                  100% VERIFIED AUTHENTIC
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Compile New Custom Dossier */}
      <ReportGeneratorModal
        aoiId="aoi-sinop-mato-grosso"
        aoiName="Sinop Deforestation Frontier (Mato Grosso)"
        isOpen={isCompileModalOpen}
        onClose={() => setIsCompileModalOpen(false)}
      />
    </div>
  );
};
