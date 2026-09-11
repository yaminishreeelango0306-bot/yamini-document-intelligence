const esc=(s)=>
  String(s??"").replace(
    /[&<>"']/g,
    (c)=>({
      "&":"&amp;",
      "<":"&lt;",
      ">":"&gt;",
      '"':"&quot;",
      "'":"&#39;"
    })[c]
  );

const label=(s)=>
  String(s??"")
    .replaceAll("_"," ")
    .replace(/\b\w/g,(c)=>c.toUpperCase());

function displayValue(value){
  if(value===null||value===undefined||value===""){
    return "Not detected";
  }

  if(typeof value==="object"){
    return JSON.stringify(value,null,2);
  }

  return String(value);
}

function getFieldValue(field){
  if(
    field&&
    typeof field==="object"&&
    Object.prototype.hasOwnProperty.call(field,"value")
  ){
    return field.value;
  }

  return field;
}

function getFieldConfidence(field){
  if(
    field&&
    typeof field==="object"&&
    typeof field.confidence==="number"
  ){
    return field.confidence;
  }

  return null;
}

function getFieldEvidence(field){
  if(
    field&&
    typeof field==="object"&&
    field.evidence
  ){
    return field.evidence;
  }

  return null;
}

function formatNumber(value){
  if(value===null||value===undefined||value===""){
    return "Not detected";
  }

  if(typeof value==="number"){
    return value.toLocaleString("en-IN");
  }

  return String(value);
}

function normalizeDocumentType(type){
  const value=String(type??"")
    .toLowerCase()
    .trim()
    .replaceAll("-","_")
    .replaceAll(" ","_");

  if(
    value==="balance_sheet"||
    value==="balancesheet"
  ){
    return "balance_sheet";
  }

  if(
    value==="profit_and_loss"||
    value==="profit_loss"||
    value==="pnl"||
    value==="p&l"
  ){
    return "profit_and_loss";
  }

  if(
    value==="cash_flow"||
    value==="cash_flow_statement"||
    value==="cashflow"
  ){
    return "cash_flow_statement";
  }

  if(value==="invoice"){
    return "invoice";
  }

  return value;
}

function statusClass(status){
  return String(status??"")
    .toLowerCase()
    .replaceAll(" ","_");
}

function renderStatus(status){
  const value=status||"UNKNOWN";

  return `
    <span class="status ${esc(statusClass(value))}">
      ${esc(value)}
    </span>
  `;
}

async function loadDocuments(){
  const body=document.getElementById("documentRows");

  if(!body){
    return;
  }

  body.innerHTML=
    "<tr><td colspan='4'>Loading...</td></tr>";

  try{
    const response=await fetch(
      "/api/v1/documents"
    );

    const data=await response.json();

    if(!response.ok){
      throw new Error(
        data?.detail?.message||
        data?.detail||
        data?.error?.message||
        "Unable to load documents"
      );
    }

    if(!Array.isArray(data)||data.length===0){
      body.innerHTML=
        "<tr><td colspan='4'>No processed documents yet.</td></tr>";
      return;
    }

    body.innerHTML=data
      .map((x)=>`
        <tr>
          <td>
            <button
              type="button"
              onclick="openDocument('${encodeURIComponent(
                x.document_name||""
              )}')"
            >
              ${esc(
                x.document_name||
                "Unknown document"
              )}
            </button>
          </td>

          <td>
            ${esc(
              label(
                x.document_type||
                "unknown"
              )
            )}
          </td>

          <td>
            ${renderStatus(
              x.processing_status||
              "UNKNOWN"
            )}
          </td>

          <td>
            ${
              x.processed_at
                ? esc(
                    new Date(
                      x.processed_at
                    ).toLocaleString()
                  )
                : "N/A"
            }
          </td>
        </tr>
      `)
      .join("");

  }catch(error){
    console.error(
      "Document loading error:",
      error
    );

    body.innerHTML=`
      <tr>
        <td colspan="4">
          Unable to load dashboard.
          ${esc(error.message)}
        </td>
      </tr>
    `;
  }
}

async function openDocument(name){
  const result=document.getElementById("result");

  if(!result){
    return;
  }

  result.classList.remove("hidden");

  result.innerHTML=
    "<p>Loading result...</p>";

  try{
    const response=await fetch(
      "/api/v1/documents/"+name
    );

    const data=await response.json();

    if(!response.ok){
      throw new Error(
        data?.error?.message||
        data?.detail?.message||
        data?.detail||
        "Unable to load document"
      );
    }

    renderResult(data,result);

    result.scrollIntoView({
      behavior:"smooth",
      block:"start"
    });

  }catch(error){
    console.error(
      "Document result error:",
      error
    );

    result.innerHTML=`
      <div class="check">
        <b>Unable to load document</b>
        <div>
          ${esc(error.message)}
        </div>
      </div>
    `;
  }
}

function renderResult(data,element){
  const fields=
    data?.extracted_data||{};

  const excludedKeys=[
    "line_items",
    "tables",
    "raw_text_by_page",
    "additional_financial_lines"
  ];

  const keys=Object.keys(fields).filter(
    (key)=>!excludedKeys.includes(key)
  );

  const pageCount=
    data?.file_validation?.page_count??
    data?.page_count??
    "N/A";

  const confidence=
    data?.overall_confidence;

  const documentType=
    normalizeDocumentType(
      data?.document_type||
      "unknown"
    );

  element.innerHTML=`
    <div class="section-head">
      <h2>
        ${esc(
          data?.document_name||
          "Document Result"
        )}
      </h2>

      ${renderStatus(
        data?.processing_status||
        "UNKNOWN"
      )}
    </div>

    <p>
      <b>Type:</b>
      ${esc(label(documentType))}

      &nbsp;&nbsp;

      <b>Confidence:</b>
      ${
        confidence!==null&&
        confidence!==undefined
          ? esc(confidence)
          : "N/A"
      }

      &nbsp;&nbsp;

      <b>Pages:</b>
      ${esc(pageCount)}
    </p>

    ${renderFileValidation(
      data?.file_validation
    )}

    <h3>Extracted Fields</h3>

    <div class="field-grid">
      ${
        keys.length
          ? keys
              .map(
                (key)=>
                  renderField(
                    key,
                    fields[key]
                  )
              )
              .join("")
          :`
            <div class="field">
              <b>No extracted fields</b>
            </div>
          `
      }
    </div>

    ${renderFinancialSummary(
      documentType,
      fields
    )}

    ${renderLineItems(
      fields.line_items||
      []
    )}

    ${renderAdditionalFinancialLines(
      fields.additional_financial_lines
    )}

    ${renderTables(
      fields.tables||
      []
    )}

    <h3>Financial Validation</h3>

    ${renderChecks(
      data?.validation
    )}

    <h3>Raw OCR Text</h3>

    ${renderRawPages(
      fields.raw_text_by_page
    )}

    <h3>Processing Metadata</h3>

    ${renderProcessingMetadata(
      data?.processing_metadata
    )}

    <h3>Raw JSON</h3>

    <pre class="json">${esc(
      JSON.stringify(
        data,
        null,
        2
      )
    )}</pre>
  `;
}

function renderFileValidation(validation){
  if(!validation){
    return "";
  }

  return `
    <div class="check">
      <b>File Validation</b>

      <div>
        File Type:
        ${esc(
          validation.file_type||
          "N/A"
        )}
      </div>

      <div>
        Supported:
        ${esc(
          String(
            validation.is_supported??
            "N/A"
          )
        )}
      </div>

      <div>
        Readable:
        ${esc(
          String(
            validation.is_readable??
            "N/A"
          )
        )}
      </div>

      <div>
        Pages:
        ${esc(
          validation.page_count??
          "N/A"
        )}
      </div>

      ${
        validation.error
          ?`
            <div>
              Error:
              ${esc(validation.error)}
            </div>
          `
          :""
      }
    </div>
  `;
}

function renderFinancialSummary(
  documentType,
  fields
){
  if(
    documentType!=="balance_sheet"&&
    documentType!=="profit_and_loss"&&
    documentType!=="cash_flow_statement"
  ){
    return "";
  }

  const summaryFields=[];

  if(documentType==="balance_sheet"){
    summaryFields.push(
      [
        "Total Assets",
        fields.total_assets
      ],
      [
        "Total Capital And Liabilities",
        fields.total_capital_and_liabilities
      ],
      [
        "Total Liabilities",
        fields.total_liabilities
      ],
      [
        "Total Equity",
        fields.total_equity
      ]
    );
  }

  if(documentType==="profit_and_loss"){
    summaryFields.push(
      [
        "Revenue",
        fields.revenue
      ],
      [
        "Total Revenue",
        fields.total_revenue
      ],
      [
        "Total Expenses",
        fields.total_expenses
      ],
      [
        "Profit Before Tax",
        fields.profit_before_tax
      ],
      [
        "Profit After Tax",
        fields.profit_after_tax
      ]
    );
  }

  if(documentType==="cash_flow_statement"){
    summaryFields.push(
      [
        "Opening Cash",
        fields.opening_cash
      ],
      [
        "Operating Cash Flow",
        fields.operating_cash_flow
      ],
      [
        "Investing Cash Flow",
        fields.investing_cash_flow
      ],
      [
        "Financing Cash Flow",
        fields.financing_cash_flow
      ],
      [
        "Net Change In Cash",
        fields.net_change_in_cash
      ],
      [
        "Closing Cash",
        fields.closing_cash
      ]
    );
  }

  const available=summaryFields.filter(
    ([,field])=>{
      const value=getFieldValue(field);

      return(
        value!==null&&
        value!==undefined&&
        value!==""
      );
    }
  );

  if(available.length===0){
    return "";
  }

  return `
    <h3>Financial Summary</h3>

    <div class="field-grid">
      ${available
        .map(
          ([name,field])=>{
            const value=getFieldValue(
              field
            );

            const confidence=
              getFieldConfidence(
                field
              );

            return `
              <div class="field">
                <b>${esc(name)}</b>

                <div class="field-value">
                  ${esc(
                    formatNumber(value)
                  )}
                </div>

                ${
                  confidence!==null
                    ?`
                      <small>
                        Confidence:
                        ${esc(confidence)}
                      </small>
                    `
                    :""
                }
              </div>
            `;
          }
        )
        .join("")}
    </div>
  `;
}

function renderField(key,field){
  const value=getFieldValue(field);

  const confidence=
    getFieldConfidence(field);

  const evidence=
    getFieldEvidence(field);

  const pageNumber=
    field&&
    typeof field==="object"
      ?field.page_number
      :null;

  const sourceText=
    evidence?.source_text||
    evidence?.text||
    "";

  const formattedValue=
    typeof value==="number"
      ?formatNumber(value)
      :displayValue(value);

  return `
    <div class="field">

      <b>${esc(label(key))}</b>

      <div class="field-value">
        ${
          typeof value==="object"&&
          value!==null
            ?`
              <pre class="json">
                ${esc(
                  JSON.stringify(
                    value,
                    null,
                    2
                  )
                )}
              </pre>
            `
            :esc(formattedValue)
        }
      </div>

      ${
        confidence!==null
          ?`
            <small>
              Confidence:
              ${esc(confidence)}
            </small>
          `
          :""
      }

      ${
        sourceText
          ?`
            <div class="evidence">
              Evidence:
              ${esc(sourceText)}

              ${
                pageNumber
                  ?` (page ${esc(
                      pageNumber
                    )})`
                  :""
              }
            </div>
          `
          :""
      }

    </div>
  `;
}

function renderLineItems(items){
  if(
    !Array.isArray(items)||
    items.length===0
  ){
    return "";
  }

  const isFinancialStatement=
    items.some(
      (item)=>
        item?.current_year!==undefined||
        item?.prior_year!==undefined||
        item?.values!==undefined
    );

  if(isFinancialStatement){
    return `
      <h3>Financial Line Items</h3>

      <div class="line-table">
        <table>

          <thead>
            <tr>
              <th>Description</th>
              <th>Current Year</th>
              <th>Previous Year</th>
              <th>Page</th>
            </tr>
          </thead>

          <tbody>
            ${items
              .map(
                (item)=>`
                  <tr>
                    <td>
                      ${esc(
                        item?.label||
                        item?.description||
                        "Not detected"
                      )}
                    </td>

                    <td>
                      ${esc(
                        formatNumber(
                          item?.current_year??
                          item?.value??
                          (
                            Array.isArray(
                              item?.values
                            )
                              ?item.values[0]
                              :null
                          )
                        )
                      )}
                    </td>

                    <td>
                      ${esc(
                        formatNumber(
                          item?.prior_year??
                          (
                            Array.isArray(
                              item?.values
                            )
                              ?item.values[1]
                              :null
                          )
                        )
                      )}
                    </td>

                    <td>
                      ${esc(
                        item?.page_number||
                        "N/A"
                      )}
                    </td>
                  </tr>
                `
              )
              .join("")}
          </tbody>

        </table>
      </div>
    `;
  }

  return `
    <h3>Line Items</h3>

    <div class="line-table">
      <table>

        <thead>
          <tr>
            <th>Description</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Amount</th>
          </tr>
        </thead>

        <tbody>
          ${items
            .map(
              (item)=>`
                <tr>

                  <td>
                    ${esc(
                      item?.description||
                      item?.label||
                      "Not detected"
                    )}
                  </td>

                  <td>
                    ${esc(
                      item?.quantity??
                      "Not detected"
                    )}
                  </td>

                  <td>
                    ${esc(
                      item?.unit_price??
                      "Not detected"
                    )}
                  </td>

                  <td>
                    ${esc(
                      item?.amount??
                      item?.value??
                      "Not detected"
                    )}
                  </td>

                </tr>
              `
            )
            .join("")}
        </tbody>

      </table>
    </div>
  `;
}

function renderAdditionalFinancialLines(field){
  const value=getFieldValue(field);

  if(
    !value||
    typeof value!=="object"||
    Object.keys(value).length===0
  ){
    return "";
  }

  const rows=Array.isArray(value)
    ?value
    :Object.values(value);

  return `
    <h3>Additional Financial Lines</h3>

    <div class="line-table">
      <table>

        <thead>
          <tr>
            <th>Detected Label</th>
            <th>Values</th>
            <th>Page</th>
            <th>Source</th>
          </tr>
        </thead>

        <tbody>
          ${rows
            .map(
              (row)=>`
                <tr>

                  <td>
                    ${esc(
                      row?.label||
                      "Not detected"
                    )}
                  </td>

                  <td>
                    ${esc(
                      Array.isArray(
                        row?.values
                      )
                        ?row.values
                            .map(
                              (value)=>
                                formatNumber(
                                  value
                                )
                            )
                            .join(" | ")
                        :formatNumber(
                            row?.values
                          )
                    )}
                  </td>

                  <td>
                    ${esc(
                      row?.page_number||
                      "N/A"
                    )}
                  </td>

                  <td>
                    ${esc(
                      row?.source_text||
                      "N/A"
                    )}
                  </td>

                </tr>
              `
            )
            .join("")}
        </tbody>

      </table>
    </div>
  `;
}

function renderTables(tables){
  if(
    !Array.isArray(tables)||
    tables.length===0
  ){
    return "";
  }

  return `
    <h3>Detected Tables</h3>

    <div class="line-table">
      <table>

        <thead>
          <tr>
            <th>Label</th>
            <th>Values</th>
            <th>Page</th>
          </tr>
        </thead>

        <tbody>
          ${tables
            .map(
              (row)=>`
                <tr>

                  <td>
                    ${esc(
                      row?.label||
                      row?.description||
                      row?.text||
                      "Detected row"
                    )}
                  </td>

                  <td>
                    ${esc(
                      Array.isArray(
                        row?.values
                      )
                        ?row.values.join(
                            " | "
                          )
                        :row?.value||
                          row?.text||
                          "N/A"
                    )}
                  </td>

                  <td>
                    ${esc(
                      row?.page_number||
                      row?.page||
                      "N/A"
                    )}
                  </td>

                </tr>
              `
            )
            .join("")}
        </tbody>

      </table>
    </div>
  `;
}

function renderRawPages(rawPages){
  if(
    !rawPages||
    typeof rawPages!=="object"
  ){
    return `
      <p>
        No raw OCR text available.
      </p>
    `;
  }

  const pages=Object.entries(
    rawPages
  );

  if(pages.length===0){
    return `
      <p>
        No raw OCR text available.
      </p>
    `;
  }

  return pages
    .map(
      ([page,text])=>`
        <div class="field">

          <b>
            Page ${esc(page)}
          </b>

          <pre class="json">${esc(
            typeof text==="string"
              ?text
              :JSON.stringify(
                  text,
                  null,
                  2
                )
          )}</pre>

        </div>
      `
    )
    .join("");
}

function renderChecks(validation){
  if(!validation){
    return `
      <p>
        No financial validation result available.
      </p>
    `;
  }

  const checks=
    Array.isArray(
      validation.checks
    )
      ?validation.checks
      :[];

  const issues=
    Array.isArray(
      validation.issues
    )
      ?validation.issues
      :[];

  const overall=
    validation.overall_status||
    "N/A";

  return `
    <p>
      <b>Overall:</b>

      ${renderStatus(overall)}
    </p>

    ${
      checks.length
        ?checks
            .map(
              (check)=>`
                <div class="check">

                  <b>
                    ${esc(
                      label(
                        check?.name||
                        "Validation Check"
                      )
                    )}

                    —
                    
                    ${esc(
                      check?.status||
                      "N/A"
                    )}
                  </b>

                  <div>
                    Formula:
                    ${esc(
                      check?.formula||
                      "N/A"
                    )}
                  </div>

                  <div>
                    Calculated:
                    ${esc(
                      formatNumber(
                        check?.calculated_value
                      )
                    )}

                    &nbsp;|&nbsp;

                    Reported:
                    ${esc(
                      formatNumber(
                        check?.reported_value
                      )
                    )}

                    &nbsp;|&nbsp;

                    Variance:
                    ${esc(
                      check?.variance??
                      "N/A"
                    )}
                  </div>

                  ${
                    check?.period
                      ?`
                        <div>
                          Period:
                          ${esc(
                            check.period
                          )}
                        </div>
                      `
                      :""
                  }

                </div>
              `
            )
            .join("")
        :`
          <p>
            No validation checks available.
          </p>
        `
    }

    ${
      issues.length
        ?`
          <div class="check">

            <b>Issues</b>

            <div>
              ${issues
                .map(
                  (issue)=>
                    esc(String(issue))
                )
                .join("<br>")}
            </div>

          </div>
        `
        :""
    }
  `;
}

function renderProcessingMetadata(metadata){
  if(!metadata){
    return `
      <p>
        No processing metadata available.
      </p>
    `;
  }

  return `
    <div class="field-grid">

      <div class="field">
        <b>OCR Used</b>

        <div class="field-value">
          ${esc(
            String(
              metadata.ocr_used??
              "N/A"
            )
          )}
        </div>
      </div>

      <div class="field">
        <b>Processed At</b>

        <div class="field-value">
          ${esc(
            metadata.processed_at||
            "N/A"
          )}
        </div>
      </div>

      <div class="field">
        <b>Processing Time</b>

        <div class="field-value">
          ${esc(
            metadata.processing_time_ms??
            "N/A"
          )} ms
        </div>
      </div>

    </div>
  `;
}

const uploadForm=
  document.getElementById(
    "uploadForm"
  );

uploadForm?.addEventListener(
  "submit",
  async(event)=>{
    event.preventDefault();

    const message=
      document.getElementById(
        "message"
      );

    const fileInput=
      document.getElementById(
        "file"
      );

    const documentType=
      document.getElementById(
        "documentType"
      );

    const result=
      document.getElementById(
        "result"
      );

    const file=
      fileInput?.files?.[0];

    const type=
      documentType?.value;

    if(!file){
      if(message){
        message.textContent=
          "Please select a file.";
      }

      return;
    }

    if(!type){
      if(message){
        message.textContent=
          "Please select a document type.";
      }

      return;
    }

    if(message){
      message.textContent=
        "Processing with PaddleOCR...";
    }

    if(result){
      result.classList.remove(
        "hidden"
      );

      result.innerHTML=`
        <div class="check">
          <b>
            Processing document...
          </b>

          <div>
            Uploading document and
            running OCR and financial
            extraction. Please wait.
          </div>
        </div>
      `;
    }

    const formData=
      new FormData();

    formData.append(
      "file",
      file
    );

    formData.append(
      "document_type",
      type
    );

    try{
      const response=
        await fetch(
          "/api/v1/documents/process",
          {
            method:"POST",
            body:formData
          }
        );

      let data;

      try{
        data=await response.json();
      }catch{
        data=null;
      }

      if(!response.ok){
        const errorMessage=
          data?.error?.message||
          data?.detail?.message||
          (
            typeof data?.detail==="string"
              ?data.detail
              :null
          )||
          data?.message||
          `Processing failed with status ${response.status}.`;

        throw new Error(
          errorMessage
        );
      }

      if(message){
        message.textContent=
          "Document processed successfully.";
      }

      if(result){
        result.classList.remove(
          "hidden"
        );

        renderResult(
          data,
          result
        );

        result.scrollIntoView({
          behavior:"smooth",
          block:"start"
        });
      }

      await loadDocuments();

    }catch(error){
      console.error(
        "Upload error:",
        error
      );

      if(message){
        message.textContent=
          error.message||
          "Unable to connect to API.";
      }

      if(result){
        result.classList.remove(
          "hidden"
        );

        result.innerHTML=`
          <div class="check">

            <b>
              Document Processing Error
            </b>

            <div>
              ${esc(
                error.message||
                "Unable to connect to API."
              )}
            </div>

          </div>
        `;
      }
    }
  }
);

loadDocuments();