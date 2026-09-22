const FEATURES = [
  {
    group: 'Loan Details',
    color: '#FFD100',
    items: [
      { name: 'AMT_INCOME_TOTAL', label: 'Annual Income', type: 'Financial', desc: 'Total verified annual income of the applicant in rupees. Higher income relative to loan amount reduces risk.', example: '₹135,000' },
      { name: 'AMT_CREDIT', label: 'Credit Amount', type: 'Financial', desc: 'Total loan amount being requested. Large loan amounts relative to income increase default risk.', example: '₹450,000' },
      { name: 'AMT_ANNUITY', label: 'Annual Annuity', type: 'Financial', desc: 'Annual repayment obligation for the requested loan. Used to compute repayment burden ratios.', example: '₹22,500' },
      { name: 'credit_income_ratio', label: 'Credit / Income Ratio', type: 'Derived', desc: 'AMT_CREDIT divided by AMT_INCOME_TOTAL. A ratio above 3.5 significantly increases default risk.', example: '3.33' },
      { name: 'annuity_income_ratio', label: 'Annuity / Income Ratio', type: 'Derived', desc: 'AMT_ANNUITY divided by AMT_INCOME_TOTAL. Measures monthly repayment burden relative to income.', example: '0.167' },
    ],
  },
  {
    group: 'Employment',
    color: '#10B981',
    items: [
      { name: 'employment_years', label: 'Employment Years', type: 'Standard', desc: 'Years of continuous verified employment at current employer. Missing values (NaN) indicate no verifiable employment history.', example: '2.5 years' },
      { name: 'NAME_INCOME_TYPE', label: 'Income Type', type: 'Categorical', desc: 'Category of employment or income source. Encoded as integer: 0=Businessman, 1=Commercial associate, 2=Maternity leave, 3=Pensioner, 4=State servant, 5=Student, 6=Unemployed, 7=Working.', example: 'Working (7)' },
    ],
  },
  {
    group: 'Payment History',
    color: '#EF4444',
    items: [
      { name: 'late_payment_share', label: 'Late Payment Share', type: 'Alternative', desc: 'Proportion of past installment payments made after the due date. Range 0–1. Above 0.2 is elevated risk.', example: '0.28 (28% of payments late)' },
      { name: 'mean_days_late', label: 'Mean Days Late', type: 'Alternative', desc: 'Average number of days payments were made past due date across all installments. Higher values indicate chronic delinquency.', example: '12.0 days' },
      { name: 'max_days_late', label: 'Max Days Late', type: 'Alternative', desc: 'Worst single late payment in days. A high maximum indicates at least one severe delinquency event.', example: '35 days' },
      { name: 'underpayment_share', label: 'Underpayment Share', type: 'Alternative', desc: 'Proportion of installments where payment made was less than amount due. Range 0–1.', example: '0.18 (18% underpaid)' },
      { name: 'installments_count', label: 'Installments Count', type: 'Alternative', desc: 'Total number of installment payments completed across all past loans. More installments = richer payment history.', example: '8 installments' },
    ],
  },
  {
    group: 'Credit Profile',
    color: '#3B82F6',
    items: [
      { name: 'prev_applications_count', label: 'Previous Applications', type: 'Standard', desc: 'Total number of prior credit applications submitted. High application frequency may indicate financial stress.', example: '3 applications' },
      { name: 'prev_refused_count', label: 'Previous Refusals', type: 'Standard', desc: 'Number of past credit applications that were declined by lenders.', example: '1 refusal' },
      { name: 'prev_refusal_rate', label: 'Refusal Rate', type: 'Derived', desc: 'prev_refused_count divided by prev_applications_count. Range 0–1. High rate signals repeated creditworthiness concerns.', example: '0.33 (1 of 3 refused)' },
      { name: 'thin_file', label: 'Thin File', type: 'Standard', desc: 'Binary flag (0 or 1). Value of 1 means the applicant has zero formal credit bureau tradelines — no credit cards, loans or lines of credit on record.', example: '1 = thin file' },
      { name: 'bureau_active_credits_count', label: 'Active Credits Count', type: 'Standard', desc: 'Number of currently active credit accounts reported to the bureau. Zero active credits combined with thin_file=1 indicates fully unbanked applicant.', example: '2 active accounts' },
    ],
  },
];

const TYPE_COLORS = {
  Financial: '#FFD100',
  Derived: '#8B5CF6',
  Alternative: '#10B981',
  Standard: '#3B82F6',
  Categorical: '#F59E0B',
};

export default function DataDictionary() {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '32px' }}>
        <div className="section-label">Reference Guide</div>
        <h2 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>Data Dictionary</h2>
        <p style={{ color: '#9CA3AF', fontSize: '15px' }}>
          Explanation of every input field used in the credit risk assessment model.
          Alternative data fields are marked in green — these are specifically designed
          to serve applicants with limited formal credit history.
        </p>
      </div>

      {/* Legend */}
      <div className="card" style={{ marginBottom: '32px', padding: '16px 20px' }}>
        <div style={{ fontSize: '13px', color: '#9CA3AF', marginBottom: '10px', fontWeight: 600 }}>
          FIELD TYPES
        </div>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          {Object.entries(TYPE_COLORS).map(([type, color]) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '3px', background: color }} />
              <span style={{ fontSize: '13px', color: '#9CA3AF' }}>{type}</span>
            </div>
          ))}
        </div>
      </div>

      {FEATURES.map(group => (
        <div key={group.group} style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px'
          }}>
            <div style={{ width: 4, height: 20, background: group.color, borderRadius: '2px' }} />
            <span style={{ fontSize: '16px', fontWeight: 700 }}>{group.group}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {group.items.map(item => (
              <div key={item.name} className="card" style={{ padding: '16px 20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                  <div>
                    <code style={{
                      fontSize: '13px', fontWeight: 700, color: '#FFD100',
                      background: 'rgba(255,209,0,0.1)', padding: '2px 8px', borderRadius: '4px',
                    }}>{item.name}</code>
                    <span style={{ fontSize: '15px', fontWeight: 600, color: '#FFFFFF', marginLeft: '10px' }}>
                      {item.label}
                    </span>
                  </div>
                  <span style={{
                    fontSize: '11px', fontWeight: 700,
                    color: TYPE_COLORS[item.type],
                    background: `${TYPE_COLORS[item.type]}15`,
                    padding: '3px 10px', borderRadius: '12px',
                    whiteSpace: 'nowrap',
                  }}>{item.type}</span>
                </div>
                <p style={{ fontSize: '14px', color: '#9CA3AF', lineHeight: 1.6, marginBottom: '8px' }}>
                  {item.desc}
                </p>
                <div style={{ fontSize: '13px', color: '#6B7280' }}>
                  Example: <span style={{ color: '#FFFFFF' }}>{item.example}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
