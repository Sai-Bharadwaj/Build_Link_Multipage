const nav=document.querySelector("#mainNav"),toggle=document.querySelector("#menuToggle");
toggle?.addEventListener("click",()=>nav.classList.toggle("open"));
document.querySelectorAll("nav a").forEach(a=>a.addEventListener("click",()=>nav?.classList.remove("open")));

const revealObserver=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add("visible")}),{threshold:.12});
document.querySelectorAll(".reveal").forEach(x=>revealObserver.observe(x));

document.querySelectorAll(".counter").forEach(el=>{
 const ob=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting)return;
  const target=+el.dataset.target,start=performance.now();
  const tick=t=>{const p=Math.min((t-start)/1100,1);el.textContent=Math.floor(p*target);if(p<1)requestAnimationFrame(tick)};
  requestAnimationFrame(tick);ob.unobserve(el);
 }),{threshold:.8});ob.observe(el);
});
function toast(msg){const t=document.querySelector("#toast");if(!t)return;t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),3000)}

function fieldLabel(field){
  const label=field.closest("label")?.textContent?.trim();
  if(label)return label;
  const placeholder=field.getAttribute("placeholder");
  if(placeholder)return placeholder;
  if(field.name)return field.name;
  if(field.tagName==="SELECT")return field.options[0]?.textContent?.trim()||"value";
  return "value";
}

function formType(form){
  const page=location.pathname.toLowerCase();
  if(page.includes("post-project"))return "project";
  if(page.includes("contractor-onboarding"))return "contractor";
  if(page.includes("find-contractors"))return "contractor-search";
  if(page.includes("messages"))return "message";
  return form.dataset.type||"form";
}

document.querySelectorAll("form.demo-form").forEach(form=>form.addEventListener("submit",async e=>{
  e.preventDefault();
  const button=form.querySelector("button[type=submit],button:not([type])");
  if(button)button.disabled=true;
  const data={};
  form.querySelectorAll("input,select,textarea").forEach(field=>{
    const value=field.value.trim();
    if(value)data[fieldLabel(field)]=value;
  });
  try{
    if(formType(form)==="contractor-search"){
      const query=new URLSearchParams({category:data["Select category"]||data.Category||"",location:data["Project location"]||data.location||""});
      const response=await fetch(`/api/search?${query}`);
      if(!response.ok)throw new Error("Search failed");
      const result=await response.json();
      toast(result.count?`${result.count} contractor${result.count===1?"":"s"} found.`:"No matching contractors yet.");
    }else{
      const response=await fetch("/api/submissions",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({page:location.pathname,form_type:formType(form),data})});
      const result=await response.json();
      if(!response.ok)throw new Error(result.error||"Unable to save submission");
      toast(form.dataset.message?.replace("in this demo","")||result.message);
      form.reset();
    }
  }catch(error){toast(error.message||"Unable to complete this action.");}
  finally{if(button)button.disabled=false;}
}));
const year=document.querySelector("#year");if(year)year.textContent=new Date().getFullYear();

// Click-to-highlight behavior for the How It Works cards.
// The selected card remains visibly highlighted briefly before navigation.
document.querySelectorAll(".interactive-card").forEach(card=>{
  card.addEventListener("click", function(e){
    document.querySelectorAll(".interactive-card").forEach(c=>c.classList.remove("selected"));
    this.classList.add("selected");

    const link=this.querySelector("a");
    if(link && link.href){
      e.preventDefault();
      setTimeout(()=>{ window.location.href=link.href; },350);
    }
  });
});

// Graceful image fallback so a broken external image never leaves a blank/broken-image area.
document.querySelectorAll("img").forEach(img=>{
  img.addEventListener("error", function(){
    this.style.display="none";
    const parent=this.parentElement;
    if(parent && !parent.querySelector(".image-fallback")){
      const fallback=document.createElement("div");
      fallback.className="image-fallback";
      fallback.textContent="BUILD LINK";
      parent.appendChild(fallback);
    }
  });
});
