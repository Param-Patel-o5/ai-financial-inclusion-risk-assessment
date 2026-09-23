const FEATURES = [
  {
    group: 'Loan & Income Details (Lane 1)',
    statute: '12 CFR § 1002.6(b)(5) — Income & Debt Obligations',
    items: [
      { name: 'amt_income_total', label: 'Annual Income', type: 'Financial', desc: 'Total verified annual income. Higher income relative to requested credit amount reduces default probability.', example: '₹85,000' },
      { name: 'amt_credit', label: 'Credit Amount', type: 'Financial', desc: 'Total loan amount requested. Large credit amounts relative to income increase debt service burden.', example: '₹520,000' },
      { name: 'amt_annuity', label: 'Annual Annuity', type: 'Financial', desc: 'Annual repayment obligation. Used to calculate payment-to-income debt ratios.', example: '₹26,000' },
      { name: 'credit_income_ratio', label: 'Credit / Income Ratio', type: 'Derived', desc: 'AMT_CREDIT divided by AMT_INCOME_TOTAL. Ratios above 3.5 significantly elevate default risk.', example: '6.12' },
      { name: 'annuity_income_ratio', label: 'Annuity / Income Ratio', type: 'Derived', desc: 'AMT_ANNUITY divided by AMT_INCOME_TOTAL. Measures ongoing monthly debt burden.', example: '0.31' },
    ],
  },
  {
    group: 'Employment & Capacity (Lane 1)',
    statute: '12 CFR § 1002.6(a) — General Rule on Evaluating Information',
    items: [
      { name: 'employment_years', label: 'Employment Years', type: 'Standard', desc: 'Years of continuous verified employment. Missing or low values reflect unstable or unverified income streams.', example: '0.8 years' },
      { name: 'name_income_type', label: 'Income Type', type: 'Categorical', desc: 'Source of employment income: 0=Businessman, 1=Commercial associate, 2=Maternity leave, 3=Pensioner, 4=State servant, 5=Student, 6=Unemployed, 7=Working.', example: 'Working (7)' },
    ],
  },
  {
    group: 'Payment & Cash Flow History (Lane 1)',
    statute: '12 CFR § 1002.6(b)(6) — Credit History Factor Authority',
    items: [
      { name: 'late_payment_share', label: 'Late Payment Share', type: 'Alternative', desc: 'Proportion of installment payments made past the scheduled due date. Values > 0.20 indicate elevated delinquency.', example: '0.42 (42% late)' },
      { name: 'mean_days_late', label: 'Mean Days Late', type: 'Alternative', desc: 'Average days past due date across all loan installments. Reflects chronic delinquency patterns.', example: '18.5 days' },
      { name: 'max_days_late', label: 'Max Days Late', type: 'Alternative', desc: 'Worst single late payment in days. Flags severe delinquency events.', example: '45.0 days' },
      { name: 'underpayment_share', label: 'Underpayment Share', type: 'Alternative', desc: 'Proportion of installments where payment made was less than amount due.', example: '0.35 (35% underpaid)' },
      { name: 'installments_count', label: 'Installments Count', type: 'Alternative', desc: 'Total installment payments completed. Low counts indicate sparse payment history.', example: '4.0 installments' },
    ],
  },
  {
    group: 'Credit Bureau & Alternative Profile (Lane 2)',
    statute: 'FCRA § 1681m(a) & CFPB Circulars 2022-03 / 2023-03',
    items: [
      { name: 'thin_file', label: 'Thin File Flag', type: 'Standard', desc: 'Binary indicator: 1 = zero formal credit bureau tradelines. Triggers alternative cash-flow scoring and regulatory boosting.', example: '1.0 (Thin-file)' },
      { name: 'bureau_active_credits_count', label: 'Active Bureau Credits', type: 'Standard', desc: 'Active credit lines reported to traditional bureaus. Zero combined with thin_file identifies unbanked borrowers.', example: '0.0 active' },
      { name: 'prev_applications_count', label: 'Previous Applications', type: 'Standard', desc: 'Prior loan applications submitted. High inquiry frequencies signal possible credit distress.', example: '5.0 applications' },
      { name: 'prev_refused_count', label: 'Previous Refusals', type: 'Standard', desc: 'Number of prior credit requests declined by lenders.', example: '3.0 refusals' },
      { name: 'prev_refusal_rate', label: 'Refusal Rate', type: 'Derived', desc: 'prev_refused_count divided by prev_applications_count. High rates indicate persistent creditworthiness issues.', example: '0.60' },
    ],
  },
];

export default function DataDictionary() {
  return (
    <div className="page-container">
      <div style={{ marginBottom: '28px' }}>
        <div style={{
          fontSize: '12px',
          fontWeight: 600,
          color: '#9CA3AF',
          letterSpacing: '0.02em',
          marginBottom: '6px',
        }}>
          Legal & Engineering Reference Guide
        </div>
        <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#FFFFFF', marginBottom: '8px' }}>
          Data Dictionary & Statutory Grounding
        </h2>
        <p style={{ color: '#9CA3AF', fontSize: '14px', margin: 0 }}>
          Complete specification of input features, derived ratios, and their governing <strong>Lane 1 (12 CFR § 1002.6)</strong> statutory authorizations.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {FEATURES.map(group => (
          <div key={group.group} style={{
            background: '#1C2333',
            border: '1px solid #2A364F',
            borderLeft: '2px solid #3B82F6',
            borderRadius: '4px',
            padding: '24px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#FFFFFF' }}>
                {group.group}
              </div>
              <div style={{
                fontSize: '11px',
                color: '#8B949E',
                background: '#161B22',
                border: '1px solid #30363D',
                padding: '4px 10px',
                borderRadius: '4px',
                fontFamily: "'IBM Plex Mono', monospace",
                fontWeight: 500,
              }}>
                {group.statute}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
              {group.items.map(item => (
                <div key={item.name} style={{
                  background: '#111111',
                  borderRadius: '4px',
                  padding: '16px',
                  border: '1px solid #222222',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <code style={{
                      fontSize: '12px',
                      color: '#8B949E',
                      fontFamily: "'IBM Plex Mono', monospace",
                    }}>
                      {item.name}
                    </code>
                    <span style={{
                      fontSize: '11px',
                      color: '#6B7280',
                      border: '1px solid #30363D',
                      padding: '1px 6px',
                      borderRadius: '3px',
                      fontFamily: "'IBM Plex Mono', monospace",
                    }}>
                      {item.type}
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#FFFFFF', marginBottom: '4px' }}>
                    {item.label}
                  </div>
                  <p style={{ fontSize: '12px', color: '#9CA3AF', lineHeight: 1.5, marginBottom: '10px' }}>
                    {item.desc}
                  </p>
                  <div style={{
                    fontSize: '11px',
                    color: '#6B7280',
                    borderTop: '1px solid #222222',
                    paddingTop: '8px',
                    fontFamily: "'IBM Plex Mono', monospace",
                  }}>
                    Example: <span style={{ color: '#6B7280', fontWeight: 400 }}>{item.example}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
