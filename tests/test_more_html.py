""" Test that passing `more_html = True` collects paragraph styles

:author: Shay Hill
:created: 11/5/2020

Paragraphs and runs can end up nested with text boxes. Docx2python
un-nests these paragraphs.

    <w:p>
        <w:pPr>
            <w:pStyle w:val="Header"/>
        </w:pPr>
        <w:r>
                <w:t>EHS Manual</w:t>
        </w:r>
        <w:r>
            <w:p>
                <w:r>
                    <w:t>EHS Manual</w:t>
                </w:r>
            </w:p>
            <w:p w14:paraId="37B5F1EE" w14:textId="1E56D065" w:rsidR="003A2388"
                w:rsidRPr="00815EC1" w:rsidRDefault="003A2388" w:rsidP="00CA47BD">
                <w:r>
                    <w:t>EHS Manual</w:t>
                </w:r>
            </w:p>
        </w:r>
        <w:r>
            <w:t>EHS Manual</w:t>
        </w:r>
    </w:p>
```
    <open par 1>
        par 1 text
        <open par 2>
            par 2 text
        <close par 2>
        more par 1 text
    <close par 1>
```

gets flattened to

```
`par 2 text`
'par 1 text`
`more par 1 text`
```
Paragraphs are returned in by the order in which they *close*.

<w:p>
    <w:pPr>
        <w:pStyle w:val="Header"/>
    </w:pPr>
    <w:r w:rsidRPr="00210F67">
        <w:rPr>
            <w:sz w:val="17"/>
            <w:szCs w:val="17"/>
        </w:rPr>
        <w:p>
            <w:r>
                <w:rPr>
                    <w:smallCaps/>
                    <w:sz w:val="72"/>
                    <w:szCs w:val="72"/>
                </w:rPr>
                <w:t>EHS Manual </w:t>
            </w:r>
        </w:p>
    </w:r>
    <w:r>
        <w:rPr>
            <w:noProof/>
        </w:rPr>
    </w:r>
</w:p>

"""

from paragraphs import par

from docx2python.iterators import iter_at_depth
from docx2python.main import docx2python
from tests.conftest import RESOURCES


def test_paragraphs_only() -> None:
    """Html tags inserted into text"""
    with docx2python(RESOURCES / "nested_paragraphs.docx", html=True) as extraction:
        document_pars = extraction.document_pars
    styled = [(p.style, p.run_strings) for p in iter_at_depth(document_pars, 4)]
    expect = [
        (
            "",
            [
                par(
                    """[Grab your reader’s attention with a great quote from the
                    document or use this space to emphasize a key point. To place
                    this text box anywhere on the page, just drag it.]"""
                )
            ],
        ),
        (
            "",
            [
                par(
                    """[Grab your reader’s attention with a great quote from the
                    document or use this space to emphasize a key point. To place
                    this text box anywhere on the page, just drag it.]"""
                )
            ],
        ),
        (
            "Heading1",
            [
                "<h1>",
                par(
                    """aaa aab aac aad aae aaf aag aah aai aaj aak aal aam aan aao
                    aap aaq aar aas aat aau aav aaw aax aay aaz aba abb abc abd abe
                    abf abg abh abi abj abk abl abm abn abo abp abq abr abs abt abu
                    abv abw abx aby abz aca acb acc acd ace acf acg ach aci acj ack
                    acl acm acn aco acp acq acr acs act acu acv acw acx acy acz ada
                    adb adc add ade adf adg adh adi adj adk adl adm adn ado adp adq
                    adr ads adt adu adv adw adx ady adz aea aeb aec aed aee aef aeg
                    aeh aei aej aek ael aem aen aeo aep aeq aer aes aet aeu aev aew
                    aex aey aez afa afb afc afd afe aff afg afh afi afj afk afl afm
                    afn afo afp afq afr afs aft afu afv afw afx afy afz aga agb agc
                    agd age agf agg agh agi agj agk agl agm agn ago agp agq agr ags
                    agt agu agv agw agx agy agz aha ahb ahc ahd ahe ahf ahg ahh ahi
                    ahj ahk ahl ahm ahn aho ahp ahq ahr ahs aht ahu ahv ahw ahx ahy
                    ahz aia aib aic aid aie aif aig aih aii aij aik ail aim ain aio
                    aip aiq air ais ait aiu aiv aiw aix aiy aiz aja ajb ajc ajd aje
                    ajf ajg ajh aji ajj ajk ajl ajm ajn ajo ajp ajq ajr ajs ajt aju
                    ajv ajw ajx ajy ajz aka akb akc akd ake akf akg akh aki akj akk
                    akl akm akn ako akp akq akr aks akt aku akv akw akx aky akz ala
                    alb alc ald ale alf alg alh ali alj alk all alm aln alo alp alq
                    alr als alt alu alv alw alx aly alz ama amb amc amd ame amf amg
                    amh ami amj amk aml amm amn amo amp amq amr ams amt amu amv amw
                    amx amy amz ana anb anc and ane anf ang anh ani anj ank anl anm
                    ann ano anp anq anr ans ant anu anv anw anx any anz aoa aob aoc
                    aod aoe aof aog aoh aoi aoj aok aol aom aon aoo aop aoq aor aos
                    aot aou aov aow aox aoy aoz apa apb apc apd ape apf apg aph api
                    apj apk apl apm apn apo app apq apr aps apt apu apv apw apx apy
                    apz aqa aqb aqc aqd aqe aqf aqg aqh aqi aqj aqk aql aqm aqn aqo
                    aqp aqq aqr aqs aqt aqu aqv aqw aqx aqy aqz ara arb arc ard are
                    arf arg arh ari arj ark arl arm arn aro arp arq arr ars art aru
                    arv arw arx ary arz asa asb asc asd ase asf asg ash asi asj ask
                    asl asm asn aso asp asq asr ass ast asu asv asw asx asy asz ata
                    atb atc atd ate atf atg ath ati atj atk atl atm atn ato atp atq
                    atr ats att atu atv atw atx aty atz aua aub auc aud aue auf aug
                    auh aui auj auk aul aum aun auo aup auq aur aus aut auu auv auw
                    aux auy auz ava avb avc avd ave avf avg avh avi avj avk avl avm
                    avn avo avp avq avr avs avt avu avv avw avx avy avz awa awb awc
                    awd awe awf awg awh awi awj awk awl awm awn awo awp awq awr aws
                    awt awu awv aww awx awy awz axa axb axc axd axe axf axg axh axi
                    axj axk axl axm axn axo axp axq axr axs axt axu axv axw axx axy
                    axz aya ayb ayc ayd aye ayf ayg ayh ayi ayj ayk ayl aym ayn ayo
                    ayp ayq ayr ays ayt ayu ayv ayw ayx ayy ayz aza azb azc azd aze
                    azf azg azh azi azj azk azl azm azn azo azp azq azr azs azt azu
                    azv azw azx azy azz"""
                ),
                "</h1>",
            ],
        ),
    ]
    assert styled == expect


def test_par_styles_not_in_text() -> None:
    """Par styles skipped in pure text export"""
    pars = docx2python(RESOURCES / "nested_paragraphs.docx", html=True)
    assert pars.text == par(
        """[Grab your reader’s attention with a great quote from the document or use
        this space to emphasize a key point. To place this text box anywhere on the
        page, just drag it.]

        [Grab your reader’s attention with a great quote from the document or use
        this space to emphasize a key point. To place this text box anywhere on the
        page, just drag it.]

        <h1>aaa aab aac aad aae aaf aag aah aai aaj aak aal aam aan aao aap aaq aar
        aas aat aau aav aaw aax aay aaz aba abb abc abd abe abf abg abh abi abj abk
        abl abm abn abo abp abq abr abs abt abu abv abw abx aby abz aca acb acc acd
        ace acf acg ach aci acj ack acl acm acn aco acp acq acr acs act acu acv acw
        acx acy acz ada adb adc add ade adf adg adh adi adj adk adl adm adn ado adp
        adq adr ads adt adu adv adw adx ady adz aea aeb aec aed aee aef aeg aeh aei
        aej aek ael aem aen aeo aep aeq aer aes aet aeu aev aew aex aey aez afa afb
        afc afd afe aff afg afh afi afj afk afl afm afn afo afp afq afr afs aft afu
        afv afw afx afy afz aga agb agc agd age agf agg agh agi agj agk agl agm agn
        ago agp agq agr ags agt agu agv agw agx agy agz aha ahb ahc ahd ahe ahf ahg
        ahh ahi ahj ahk ahl ahm ahn aho ahp ahq ahr ahs aht ahu ahv ahw ahx ahy ahz
        aia aib aic aid aie aif aig aih aii aij aik ail aim ain aio aip aiq air ais
        ait aiu aiv aiw aix aiy aiz aja ajb ajc ajd aje ajf ajg ajh aji ajj ajk ajl
        ajm ajn ajo ajp ajq ajr ajs ajt aju ajv ajw ajx ajy ajz aka akb akc akd ake
        akf akg akh aki akj akk akl akm akn ako akp akq akr aks akt aku akv akw akx
        aky akz ala alb alc ald ale alf alg alh ali alj alk all alm aln alo alp alq
        alr als alt alu alv alw alx aly alz ama amb amc amd ame amf amg amh ami amj
        amk aml amm amn amo amp amq amr ams amt amu amv amw amx amy amz ana anb anc
        and ane anf ang anh ani anj ank anl anm ann ano anp anq anr ans ant anu anv
        anw anx any anz aoa aob aoc aod aoe aof aog aoh aoi aoj aok aol aom aon aoo
        aop aoq aor aos aot aou aov aow aox aoy aoz apa apb apc apd ape apf apg aph
        api apj apk apl apm apn apo app apq apr aps apt apu apv apw apx apy apz aqa
        aqb aqc aqd aqe aqf aqg aqh aqi aqj aqk aql aqm aqn aqo aqp aqq aqr aqs aqt
        aqu aqv aqw aqx aqy aqz ara arb arc ard are arf arg arh ari arj ark arl arm
        arn aro arp arq arr ars art aru arv arw arx ary arz asa asb asc asd ase asf
        asg ash asi asj ask asl asm asn aso asp asq asr ass ast asu asv asw asx asy
        asz ata atb atc atd ate atf atg ath ati atj atk atl atm atn ato atp atq atr
        ats att atu atv atw atx aty atz aua aub auc aud aue auf aug auh aui auj auk
        aul aum aun auo aup auq aur aus aut auu auv auw aux auy auz ava avb avc avd
        ave avf avg avh avi avj avk avl avm avn avo avp avq avr avs avt avu avv avw
        avx avy avz awa awb awc awd awe awf awg awh awi awj awk awl awm awn awo awp
        awq awr aws awt awu awv aww awx awy awz axa axb axc axd axe axf axg axh axi
        axj axk axl axm axn axo axp axq axr axs axt axu axv axw axx axy axz aya ayb
        ayc ayd aye ayf ayg ayh ayi ayj ayk ayl aym ayn ayo ayp ayq ayr ays ayt ayu
        ayv ayw ayx ayy ayz aza azb azc azd aze azf azg azh azi azj azk azl azm azn
        azo azp azq azr azs azt azu azv azw azx azy azz</h1>"""
    )
    pars.close()


class TestBulletedLists:
    """Replace numbering format with bullet (--) when format cannot be determined"""

    def test_bulleted_lists(self) -> None:
        pars = docx2python(RESOURCES / "created-in-pages-bulleted-lists.docx")
        assert pars.text == (
            "\n\nThis is a document for testing docx2python module.\n\n\n\n--\tWhy "
            "did the chicken cross the road?\n\n\t--\tJust because\n\n\t--\tDon't "
            "know\n\n\t--\tTo get to the other side\n\n--\tWhat's the meaning of life, "
            "universe and everything?\n\n\t--\t42\n\n\t--\t0\n\n\t--\t-1\n\n"
        )
        pars.close()
