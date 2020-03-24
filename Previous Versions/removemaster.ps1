$Input = "C:\Users\patrick.talley\Desktop\new.xspt"
$Output = "C:\Users\patrick.talley\Desktop\new.xspt"

# Load the existing document
$Doc = [xml](Get-Content $Input)

# Specify tag names to delete and then find them
$DeleteNames = "DAProductLib1\Communications\Routing", "DAProductLib1\Communications\WiFi", "DAProductLib1\Communications\Ethernet", "DAProductLib1\Communications\Serial", "DAProductLib1\Communications\DNP"
($Doc.AppData.ChildNodes |Where-Object { $DeleteNames -contains $_.Uri }) | ForEach-Object {
    # Remove each node from its parent
    [void]$_.ParentNode.RemoveChild($_)
}

# Save the modified document
$Doc.Save($Output)