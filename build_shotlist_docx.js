// shotlist.json → L5Y-Shot-List.docx (landscape, one table per status group)
const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,AlignmentType,
       ShadingType,PageOrientation,BorderStyle}=require('docx');
const S=JSON.parse(fs.readFileSync('shotlist.json','utf8'));
const INK='1a1d26', GOLD='8a6d10', DIM='6b7280', PINK='c2447a';
const MONO='Courier New', BODY='Georgia';
const kids=[];
const P=(t,o={})=>new Paragraph({spacing:{after:o.after??80},children:[new TextRun({text:t,font:o.mono?MONO:BODY,size:o.size||19,bold:!!o.bold,italics:!!o.italics,color:o.color||INK})]});

kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:200,after:40},
  children:[new TextRun({text:'THE LAST FIVE YEARS · THE SECOND SCREEN',font:MONO,size:20,color:PINK,bold:true})]}));
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:60},
  children:[new TextRun({text:'Shot List & Asset Naming',font:BODY,size:52,bold:true,color:INK})]}));
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:260},
  children:[new TextRun({text:'Every photo, video and audio file the show needs — what to shoot, and the exact filename to upload.',font:BODY,size:19,italics:true,color:DIM})]}));

kids.push(P('HOW TO NAME AND UPLOAD',{mono:true,size:18,bold:true,color:DIM}));
const N=S.naming;
[['Naming rule',N.rule],['Examples',N.examples.join('   ')],['Photos',N.photos],['Video',N.video],['Audio',N.audio],['Where',N.folder]]
  .forEach(([k,v])=>kids.push(new Paragraph({spacing:{after:70},children:[
    new TextRun({text:k+':  ',font:MONO,size:17,bold:true,color:GOLD}),new TextRun({text:v,font:BODY,size:18,color:INK})]})));

const ext={photo:'jpg',video:'mp4',audio:'m4a'};
const fname=(a,c)=>`S${String(a.song).padStart(2,'0')}-${a.code}-${a.slug}-${c}.${ext[a.kind]}`;
const filesFor=a=>a.status==='derived'?'— (made from M7)':a.shared?fname(a,'SHARED'):`${fname(a,'ML')}\n${fname(a,'AC')}`;
const cell=(t,w,o={})=>new TableCell({width:{size:w,type:WidthType.PERCENTAGE},shading:o.fill?{type:ShadingType.CLEAR,fill:o.fill}:undefined,
  margins:{top:60,bottom:60,left:90,right:90},
  children:String(t).split('\n').map(line=>new Paragraph({children:[new TextRun({text:line,font:o.mono?MONO:BODY,size:o.size||15,bold:!!o.bold,color:o.color||INK})]}))});
const groups=[['confirmed','SHOOT NOW — confirmed for the locked build','e8f0e4'],['derived','DERIVED — nothing to shoot','eef0f4'],['pending','HOLD — depends on the Song 10–14 answers','faf3dc']];
for(const [status,heading,fill] of groups){
  const rows=S.assets.filter(a=>a.status===status); if(!rows.length) continue;
  kids.push(new Paragraph({spacing:{before:320,after:100},children:[new TextRun({text:heading,font:BODY,size:26,bold:true,color:INK})]}));
  const W=[6,12,14,32,9,9,10,8];
  const head=new TableRow({tableHeader:true,children:['Code','Upload as','What it is','Shoot this','Who','Era','Format','Appears in']
    .map((h,i)=>cell(h,W[i],{fill,mono:true,bold:true,size:14,color:DIM}))});
  const body=rows.map(a=>new TableRow({children:[
    cell(a.code,W[0],{mono:true,bold:true,size:17}),cell(filesFor(a),W[1],{mono:true,size:14,color:GOLD}),
    cell(a.title,W[2],{bold:true}),cell(a.shoot,W[3]),cell(a.who,W[4]),cell(a.era,W[5]),cell(a.format,W[6]),cell(a.appears,W[7])]}));
  kids.push(new Table({width:{size:100,type:WidthType.PERCENTAGE},rows:[head,...body]}));
}
const doc=new Document({styles:{default:{document:{run:{font:BODY,size:18,color:INK}}}},
  sections:[{properties:{page:{size:{width:15840,height:12240,orientation:PageOrientation.LANDSCAPE},margin:{top:800,bottom:800,left:800,right:800}}},children:kids}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('L5Y-Shot-List.docx',b);console.log('L5Y-Shot-List.docx written');});
