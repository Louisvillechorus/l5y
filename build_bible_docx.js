const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,HeadingLevel,AlignmentType,ShadingType,
       Header,Footer,PageNumber,BorderStyle}=require('docx');
const B=JSON.parse(fs.readFileSync('bible.json','utf8'));

const INK='1a1d26', GOLD='8a6d10', DIM='6b7280', PINK='c2447a', BLUE='2a5db0';
const MONO='Courier New', BODY='Georgia', HEAD='Georgia';


const kids=[];

// ---- title block ----
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:600,after:60},
  children:[new TextRun({text:'THE LAST FIVE YEARS · THE SECOND SCREEN',font:MONO,size:22,color:PINK,bold:true})]}));
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:120},
  children:[new TextRun({text:'The Cue Bible',font:HEAD,size:72,bold:true,color:INK})]}));
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:40},
  children:[new TextRun({text:B.build,font:MONO,size:18,color:DIM})]}));
kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{after:260},
  children:[new TextRun({text:`${B.songs.reduce((a,s)=>a+s.fires,0)} cues · ${B.songs.length} songs · generated from the live show build, so this document cannot drift from what the phones actually do`,
    font:BODY,size:19,italics:true,color:DIM})]}));

kids.push(new Paragraph({spacing:{after:100},shading:{type:ShadingType.CLEAR,fill:'f2ede2'},
  children:[new TextRun({text:'THE STANDING RULE: the phone behaves exactly like a real phone. ',bold:true,font:BODY,size:20,color:INK}),
            new TextRun({text:'Tapping a notification IS the unlock — the app opens directly, no home screen. Inboxes and message lists load whole the instant the app opens, and a full life continues past the bottom edge of the glass. Only what would genuinely arrive right now — a text, a notification, new mail — appears live, and new mail lands at the top. Anything that violates this is a bug, even if it would make a nice theatrical beat.',font:BODY,size:20,color:INK})]}));
kids.push(new Paragraph({spacing:{after:320},
  children:[new TextRun({text:'How to read each entry: the header gives the cue ID, which screen, whose phone, the app, and the musical anchor. ON SCREEN is the complete content, verbatim and untruncated. PLAYS covers mechanics the engine performs on its own — navigation, self-timed animation, synthesized sound. PHONES gives the state after the cue when it changed. Gold notes carry dramaturgy, holds, and open director choices.',
    font:BODY,size:18,italics:true,color:DIM})]}));

const label=(t)=>new TextRun({text:t,font:MONO,size:16,bold:true,color:DIM});

for(const s of B.songs){
  const sings = s.who==='both' ? 'BOTH SING' : (s.who==='cathy'?'CATHY SINGS':'JAMIE SINGS');
  kids.push(new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:s.n>1,spacing:{before:200,after:60},
    children:[new TextRun({text:`${s.n} · ${s.t}`,font:HEAD,size:40,bold:true,color:INK}),
              new TextRun({text:`   ${sings} · ${s.fires} FIRES`,font:MONO,size:18,color:PINK})]}));
  kids.push(new Paragraph({spacing:{after:200},shading:{type:ShadingType.CLEAR,fill:'eef0f4'},
    children:[new TextRun({text:s.intro||'',font:BODY,size:19,color:INK})]}));

  let prevApp=null, prevStamp=null;
  for(const c of s.cues){
    // entry header
    kids.push(new Paragraph({spacing:{before:200,after:40},keepNext:true,
      border:{top:{style:BorderStyle.SINGLE,size:4,color:'d8d2c2'}},
      children:[new TextRun({text:`${c.id}`,font:MONO,size:22,bold:true,color:INK}),
                new TextRun({text:`  ${c.screen} · ${c.who}${c.black?'':' · '+c.app}`,font:MONO,size:17,color:BLUE}),
                new TextRun({text:`   —  ${c.trig}`,font:BODY,size:19,italics:true,color:INK})]}));
    // dramaturgy line (what)
    if(c.what) kids.push(new Paragraph({spacing:{after:60},keepNext:true,
      children:[new TextRun({text:c.what,font:BODY,size:19,color:'3a3f4d'})]}));
    // ON SCREEN
    if(c.content.length){
      kids.push(new Paragraph({spacing:{after:20},keepNext:true,children:[label('ON SCREEN')]}));
      for(const [pre,txt] of c.content){
        kids.push(new Paragraph({spacing:{after:14},indent:{left:280},
          children:[new TextRun({text:pre,font:MONO,size:18,bold:true,color:INK}),
                    new TextRun({text:txt,font:MONO,size:18,color:INK})]}));
      }
    }
    // PLAYS
    if(c.plays.length){
      kids.push(new Paragraph({spacing:{before:30,after:20},keepNext:true,children:[label('PLAYS')]}));
      for(const p of c.plays) kids.push(new Paragraph({spacing:{after:14},indent:{left:280},
        children:[new TextRun({text:p,font:BODY,size:18,color:'3a3f4d'})]}));
    }
    // SOUND (for the sound op — synthesized or practical, director's choice)
    if(c.sound && c.sound.length){
      kids.push(new Paragraph({spacing:{before:26,after:20},keepNext:true,children:[label('SOUND')]}));
      for(const p of c.sound) kids.push(new Paragraph({spacing:{after:14},indent:{left:280},
        children:[new TextRun({text:p,font:BODY,size:18,color:'6a5a20'})]}));
    }
    // PHONES (state after, when it moved)
    if(!c.black && (c.app!==prevApp || c.stamp!==prevStamp)){
      kids.push(new Paragraph({spacing:{before:30,after:14},
        children:[label('PHONES  '),
          new TextRun({text:`${c.screen} = ${c.app}` + (c.stamp?`  ·  stamp “${c.stamp}”`:'') + (c.clock?`  ·  clock ${c.clock}`:''),
            font:MONO,size:17,color:DIM})]}));
    }
    prevApp=c.app; prevStamp=c.stamp;
    // gold notes
    if(c.hold) kids.push(new Paragraph({spacing:{before:30,after:14},shading:{type:ShadingType.CLEAR,fill:'faf3dc'},
      children:[new TextRun({text:'HOLD · ',font:MONO,size:17,bold:true,color:GOLD}),
                new TextRun({text:c.hold,font:BODY,size:18,italics:true,color:GOLD})]}));
    if(c.cut) kids.push(new Paragraph({spacing:{before:20,after:14},shading:{type:ShadingType.CLEAR,fill:'faf3dc'},
      children:[new TextRun({text:'CUTAWAY · ',font:MONO,size:17,bold:true,color:GOLD}),
                new TextRun({text:c.cut,font:BODY,size:18,italics:true,color:GOLD})]}));
  }
}

const doc=new Document({styles:{default:{document:{run:{font:BODY,size:19,color:INK}}}},
 sections:[{properties:{page:{size:{width:12240,height:15840},margin:{top:1000,bottom:1000,left:1100,right:1100}}},
  headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,
    children:[new TextRun({text:'L5Y · THE SECOND SCREEN — CUE BIBLE',font:MONO,size:14,color:DIM})]})]})},
  footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,
    children:[new TextRun({children:[PageNumber.CURRENT],font:MONO,size:14,color:DIM})]})]})},
  children:kids}]});

Packer.toBuffer(doc).then(b=>{fs.writeFileSync('L5Y-Cue-Bible.docx',b);console.log('docx written');});
