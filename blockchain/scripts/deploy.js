async function main() {
  const Registry = await ethers.getContractFactory("DataRegistry");
  const registry = await Registry.deploy();

  await registry.deployed();

  console.log("DataRegistry deployed to:", registry.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
